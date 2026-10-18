"""Fixed Manim tensor diagrams. JSON is display data, never Python or LaTeX."""
import json
import os
import re
from pathlib import Path

import numpy as np
from manim import (
    Scene, Text, VGroup, RoundedRectangle, Rectangle, Arrow, Line, Dot,
    FadeIn, FadeOut, Transform, ReplacementTransform, Create,
    LEFT, RIGHT, UP, DOWN, WHITE, BLUE_C, TEAL_C, GOLD_C, GREY_B,
)

MAX_SPEC_BYTES = 256 * 1024


def load_spec():
    path = Path(os.environ.get('PAPERLOOM_TENSOR_SPEC', ''))
    if not path.is_file() or path.stat().st_size > MAX_SPEC_BYTES:
        raise ValueError('PAPERLOOM_TENSOR_SPEC must name a JSON file <=256 KiB')
    spec = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(spec, dict) or not isinstance(spec.get('step'), dict):
        raise ValueError('spec.step must be an object')
    return spec


def label(value, limit=1800):
    if not isinstance(value, (str, int, float)):
        return '확인 불가'
    return ''.join(c for c in str(value) if c >= ' ' or c == '\n')[:limit]


def write_progress(index, total):
    target = os.environ.get('PAPERLOOM_TENSOR_PROGRESS')
    if not target:
        return
    path = Path(target)
    temporary = path.with_name(path.name + '.tmp-' + str(os.getpid()))
    temporary.write_text(json.dumps({'progress': 10 + int(80 * index / max(1, total)),
                                      'stage': f'연산 {index}/{total} 렌더링'}, ensure_ascii=False), encoding='utf-8')
    os.replace(temporary, path)


def matches_dreamzero_profile(profile):
    if not isinstance(profile, dict):
        return False
    if profile.get('repository') != 'https://github.com/dreamzero0/dreamzero':
        return False
    if profile.get('commit') != 'ab790c198fbce33503358efbbd4187ce9a89adf3':
        return False
    if profile.get('config') not in ('groot/vla/configs/conf.yaml', 'scripts/train/droid_training_lora.sh'):
        return False
    dimensions = profile.get('dimensions')
    if not isinstance(dimensions, list):
        return False
    parsed = {}
    for item in dimensions[:100]:
        if not isinstance(item, dict):
            continue
        symbols = str(item.get('symbol', '')).split(';')
        values = str(item.get('value', '')).split(';')
        if len(symbols) != len(values):
            continue
        for symbol, value in zip(symbols, values):
            symbol, value = symbol.strip(), value.strip()
            # Accept literal leading values, never evaluate equations or expressions.
            match = re.match(r'^(?:[A-Za-z_]+\s*=\s*)?(\d+)(?=$|[\s;=])', value)
            if match:
                number = int(match[1])
                if symbol in parsed and parsed[symbol] != number:
                    return False
                parsed[symbol] = number
            if symbol == 'Hview × Wview' and re.fullmatch(r'176\s*×\s*320', value):
                parsed['H_view'], parsed['W_view'] = 176, 320
    required = [(('D',), 5120), (('heads', 'H_attn', 'n_heads'), 40),
                (('H_view',), 176), (('W_view',), 320),
                (('C_in', 'Cin'), 36), (('C_z', 'Cz'), 16),
                (('D_action_pad', 'Da'), 32)]
    for aliases, expected in required:
        present = [parsed[k] for k in aliases if k in parsed]
        if not present or any(value != expected for value in present):
            return False
    if 'dh' in parsed and parsed['dh'] != 128:
        return False
    return True


def operation_kind(row):
    value = ' '.join(label(row.get(k, ''), 4000) for k in ('title', 'operation', 'equation')).casefold()
    for kind, words in (
        ('loss', ('loss', 'mse', 'mean(', '축약', '평균')),
        ('attention', ('attention', 'qkv', 'softmax', 'einsum', 'q/k/v')),
        ('permute', ('permute', 'transpose', '축 전환', '축 교환')),
        ('patch', ('patch', 'conv3d', '격자', 'unpatch')),
        ('concat', ('concat', 'cat(', '결합', 'prefix')),
        ('split', ('split', 'chunk(', '분리', 'slice')),
        ('sampler', ('scheduler', 'unipc', 'predictor', 'corrector', 'sigma', '반복')),
        ('head', ('linear', 'projection', 'projector', 'head', 'mlp', 'w1', 'w2')),
    ):
        if any(word in value for word in words):
            return kind
    return 'transform'


class TensorTraceScene(Scene):
    def construct(self):
        self.camera.background_color = '#151b24'
        spec = load_spec()
        step = spec['step']
        font = 'AppleGothic'

        def text(value, size=22, color=WHITE, width=12.4):
            value = label(value)
            # Wrap labels without interpreting any markup, LaTeX or commands.
            lines = []
            for paragraph in value.split('\n'):
                while len(paragraph) > 64:
                    cut = paragraph.rfind(' ', 20, 64)
                    cut = cut if cut > 20 else 64
                    lines.append(paragraph[:cut])
                    paragraph = paragraph[cut:].lstrip()
                lines.append(paragraph)
            result = Text('\n'.join(lines) or '확인 불가', font=font, font_size=size, color=color,
                          disable_ligatures=True, line_spacing=.7)
            if result.width > width:
                result.scale_to_fit_width(width)
            return result

        title = text(step.get('title', 'Tensor trace'), 30).to_edge(UP, buff=.35)
        mode = spec.get('mode', step.get('mode', 'shared'))
        mode_name = {'training': '학습', 'inference': '추론', 'shared': '공통'}.get(mode, '확인 불가')
        subtitle = text(f'{mode_name} · 코드 기반 shape 도식 · 실제 모델 실행 아님', 17, GREY_B).next_to(title, DOWN, buff=.16)
        footer = text('블록 수는 표시용 압축입니다. 실제 원소 수·값·연산 속도를 나타내지 않습니다.', 16, GREY_B).to_edge(DOWN, buff=.25)
        self.add(title, subtitle, footer)
        rows = [r for r in step.get('shape_trace', []) if isinstance(r, dict)] if isinstance(step.get('shape_trace'), list) else []
        if not rows:
            rows = [step]
        count = len(rows)
        row_index = spec.get('row_index')
        if row_index is not None:
            if not isinstance(row_index, int) or isinstance(row_index, bool) or not 0 <= row_index < count:
                raise ValueError('row_index is outside step.shape_trace')
            rows = [rows[row_index]]
        else:
            rows = rows[:6]
        caption = text((f'선택 연산 {row_index+1}/{count}' if row_index is not None else f'{len(rows)}개 연산 표시') + (f' / 전체 {count}개 · 나머지는 텍스트 trace 참조' if count > 6 and row_index is None else ''), 16, GREY_B).next_to(subtitle, DOWN, buff=.1)
        self.add(caption)
        input_title = text('입력', 18, BLUE_C).move_to([-3.5, 1.65, 0])
        output_title = text('출력', 18, TEAL_C).move_to([3.5, 1.65, 0])
        self.add(input_title, output_title)

        def block(x, y, color=BLUE_C):
            return RoundedRectangle(width=.62, height=.48, corner_radius=.06,
                                    stroke_color=color, fill_color=color, fill_opacity=.24).move_to([x, y, 0])

        def grid(center, color, columns=3, total=6):
            return VGroup(*(block(center[0] + (i % columns - (columns-1)/2)*.75,
                                 center[1] + (.5 - i//columns)*.61, color)
                            for i in range(total)))

        old = None
        duration = min(3.5, 6.3 / len(rows))
        for index, row in enumerate(rows):
            write_progress(index, len(rows))
            shapes = VGroup(
                text(row.get('input_shape', step.get('input_shape', '확인 불가')), 19, BLUE_C, 5.8).move_to([-3.5, .85, 0]),
                text(row.get('output_shape', step.get('output_shape', '확인 불가')), 19, TEAL_C, 5.8).move_to([3.5, .85, 0]),
            )
            for item in shapes:
                if item.height > .9:
                    item.scale_to_fit_height(.9)
            operation = text(f'{index+1}/{count} · '+label(row.get('title', '연산')), 21).move_to([0, -1.7, 0])
            detail = text(row.get('operation') or row.get('equation') or step.get('operation', ''), 17, GREY_B).move_to([0, -2.35, 0])
            if detail.height > .75:
                detail.scale_to_fit_height(.75)
            arrow = Arrow([-1.3, -.45, 0], [1.3, -.45, 0], buff=.12, color=GREY_B)
            kind = operation_kind(row)
            if row.get('basis') == 'unknown' or '확인 불가' in label(row.get('output_shape', '')):
                kind = 'unknown'
            notice = text('확인 불가 경계 · 물리 실행을 재현하지 않습니다.' if kind == 'unknown' else
                          '연결선은 연산 흐름 도식이며 실제 attention mask·가중치가 아닙니다.', 13, GREY_B).move_to([0, -2.95, 0])
            left = grid((-3.5, -.45), BLUE_C)
            right = grid((3.5, -.45), TEAL_C)
            content = VGroup(shapes, operation, detail, arrow, left, right, notice)
            if old is not None:
                self.remove(*self.mobjects)
                self.add(title, subtitle, footer, caption, input_title, output_title)
            self.add(shapes, operation, detail, arrow, left, notice)
            context = ' '.join(label(row.get(k, ''), 4000) for k in ('title', 'operation', 'input_shape', 'output_shape')).casefold()
            profile = spec.get('profile') or {}
            verified_profile = matches_dreamzero_profile(profile)
            specific = None
            if verified_profile and kind != 'unknown':
                if '257' in context and '512' in context and ('cross' in context or 'context' in context) and ('attention' in context or 'softmax' in context):
                    specific = 'cross'
                elif '5120' in context and ('qkv' in context or 'q,k,v' in context or 'q/k/v' in context or 'head' in context and '128' in context):
                    specific = 'qkv'
                elif ('patch_embedding' in context or 'conv3d' in context or 'patch' in context) and '36' in context and '5120' in context:
                    specific = 'patch'
                elif ('b t h w c' in context or 'b,t,h,w,c' in context or 'b,t,352,640,3' in context) and ('permute' in context or 'rearrange' in context or 'transpose' in context):
                    specific = 'axes'
                elif mode != 'inference' and 'cat' in context and ('register' in context or 'state' in context) and ('5120' in context or '영상' in context):
                    specific = 'concat'
                elif 'mean(dim=(1,3,4))' in context or 'mean(dim=2)' in context:
                    specific = 'loss'
                elif 'd1s' in context and ('einsum' in context or 'history' in context):
                    specific = 'history'
            if specific:
                self.remove(left, arrow)
                def box_label(caption_value, center, width=2.4, color=BLUE_C):
                    rect = RoundedRectangle(width=width, height=.65, corner_radius=.07, stroke_color=color, fill_color=color, fill_opacity=.15).move_to(center)
                    txt = text(caption_value, 17, color, width-.12).move_to(center)
                    return VGroup(rect, txt)
                if specific == 'cross':
                    query=box_label('Q [B,L,40,128]',[-4,-.4,0],2.8)
                    txt=box_label('text 512 · softmax',[-.25,.1,0],3,BLUE_C)
                    img=box_label('image 257 · softmax',[-.25,-.85,0],3,TEAL_C)
                    result=box_label('합산 → output',[4,-.4,0],2.7,GOLD_C)
                    self.add(query)
                    self.play(FadeIn(txt),FadeIn(img),run_time=duration*.5)
                    self.play(Create(Arrow(txt.get_right(),result.get_left(),buff=.1)),Create(Arrow(img.get_right(),result.get_left(),buff=.1)),FadeIn(result),run_time=duration*.5)
                    self.add(text('512+257 토큰을 하나의 softmax로 정규화하지 않습니다.',17,GREY_B).move_to([0,-1.35,0]))
                elif specific == 'qkv':
                    self.remove(notice)
                    notice = text('정확히 40개 head · head당 128차원 · 각 사각형은 head 하나', 14, GREY_B).move_to([0,-2.95,0]); self.add(notice)
                    src = box_label('[B,L,5120]', [-3.7,-.45,0])
                    targets = VGroup()
                    for ri, name in enumerate(('Q','K','V')):
                        y=.15-ri*.46
                        slabs=VGroup(*(Rectangle(width=.095,height=.31,stroke_width=.5,stroke_color=TEAL_C,fill_color=TEAL_C,fill_opacity=.3).move_to([.5+j*.12,y,0]) for j in range(40)))
                        targets.add(slabs,text(name,17,TEAL_C).move_to([0,y,0]))
                    self.add(src)
                    self.play(FadeIn(targets,shift=RIGHT*.4),run_time=duration*.7)
                    self.play(src.animate.set_color(GOLD_C),run_time=duration*.3)
                elif specific == 'patch':
                    src=box_label('36 × 1 × 2 × 2 = 144',[-3.6,-.35,0],3.4)
                    dst=box_label('학습된 투영 → 5120', [3.5,-.35,0],3.2,TEAL_C)
                    spatial=text('latent 44×80 → patch grid 22×40 → 880 tokens/frame',18,GREY_B).move_to([0,-1.15,0])
                    connector=Arrow(src.get_right(),dst.get_left(),buff=.12,color=GREY_B)
                    self.add(src,spatial);self.play(Create(connector),FadeIn(dst),run_time=duration)
                elif specific == 'axes':
                    axes=['B','T','H','W','C'];target_order=['B','C','T','H','W']
                    tokens=VGroup(*(box_label(a,[-4.9+i*1.1,-.2,0],.85) for i,a in enumerate(axes)))
                    self.add(tokens)
                    note=text('permute(0,4,1,2,3) · 값 계산 없이 축과 stride 해석 이동',17,GREY_B).move_to([0,-1.05,0]);self.add(note)
                    self.play(*[tokens[i].animate.move_to([.4+target_order.index(a)*1.1,-.2,0]).set_color(TEAL_C) for i,a in enumerate(axes)],run_time=duration)
                elif specific == 'concat':
                    segments=VGroup(box_label('영상: 880F',[-3.6,.2,0],2.6),box_label('행동: 24K',[-3.6,-.55,0],2.6,TEAL_C),box_label('상태: K',[-3.6,-1.3,0],2.6,GOLD_C))
                    self.add(segments)
                    self.play(*[seg.animate.move_to([-.1+i*2.1,-.45,0]).scale(.75) for i,seg in enumerate(segments)],run_time=duration)
                    self.add(text('token 축: 880F + 24K + K · 특징 폭 5120 유지',17,GREY_B).move_to([0,-1.25,0]))
                elif specific == 'loss':
                    video='mean(dim=(1,3,4))' in context
                    src=box_label('[B,16,F,44,80]' if video else '[B,A,32]',[-3.8,-.3,0],3)
                    reduced=box_label('[B,F]' if video else '[B,A]',[0,-.3,0],1.8,TEAL_C)
                    scalar=box_label('scalar',[3.6,-.3,0],1.7,GOLD_C)
                    self.add(src)
                    self.play(Transform(src.copy(),reduced),run_time=duration*.5)
                    self.play(FadeIn(scalar),Create(Arrow(reduced.get_right(),scalar.get_left(),buff=.1)),run_time=duration*.5)
                    self.add(text('C,H,W 축 평균 → timestep 가중치 → B,F 평균' if video else 'mask 적용 → padded32 축 평균 → timestep 가중치 → B,A 평균',17,GREY_B).move_to([0,-1.15,0]))
                else:
                    history=box_label('D1s [B,q,C,…]',[-3.8,-.35,0],3)
                    coeff=box_label('ρ [q]',[0,.1,0],1.5,GOLD_C)
                    result=box_label('Σq ρq D1sq',[3.5,-.35,0],3,TEAL_C)
                    self.add(history,coeff)
                    self.play(Create(Arrow(history.get_right(),result.get_left(),buff=.12)),FadeIn(result),run_time=duration)
                    self.add(text('UniPC history 축 q만 축약 · sample 축 보존 · 실제 계수/값 미측정',16,GREY_B).move_to([0,-1.2,0]))
            elif kind == 'unknown':
                self.remove(arrow)
                self.add(right)
                self.wait(duration)
            elif kind == 'permute':
                target = grid((3.5, -.45), TEAL_C, columns=2)
                self.play(*[left[i].animate.move_to(target[(i % 3)*2+i//3].get_center()).set_color(TEAL_C)
                            for i in range(6)], run_time=duration)
            elif kind in ('loss', 'head'):
                target = VGroup(block(3.5, -.45, TEAL_C)) if kind == 'loss' else grid((3.5, -.45), TEAL_C, columns=2, total=4)
                self.play(ReplacementTransform(left, target), run_time=duration)
                content.add(target)
            elif kind == 'concat':
                colors = [BLUE_C, BLUE_C, TEAL_C, TEAL_C, GOLD_C, GOLD_C]
                for i, item in enumerate(left):
                    item.set_color(colors[i])
                targets = [np.array([2.0 + i*.6, -.45, 0]) for i in range(6)]
                self.play(*[item.animate.move_to(targets[i]).scale(.8) for i, item in enumerate(left)], run_time=duration)
            elif kind == 'split':
                self.play(*[item.animate.move_to([3.15+(i%2)*.8, .15-(i//2)*.62, 0]).set_color([BLUE_C,TEAL_C,GOLD_C][i//2])
                            for i,item in enumerate(left)], run_time=duration)
            elif kind == 'attention':
                self.add(right)
                edges = VGroup(*(Line(left[i].get_right(), right[j].get_left(), stroke_width=1,
                                     stroke_opacity=.3, color=GOLD_C) for i in range(6) for j in range(6)))
                content.add(edges)
                self.play(Create(edges), run_time=duration*.5)
                self.play(*[r.animate.set_fill(TEAL_C, opacity=.65) for r in right], run_time=duration*.5)
            elif kind == 'sampler':
                self.add(right)
                token = Dot(arrow.get_start(), color=GOLD_C, radius=.09)
                content.add(token);self.add(token)
                self.play(token.animate.move_to(arrow.get_end()), *[r.animate.set_fill(TEAL_C, opacity=.6) for r in right], run_time=duration)
            elif kind == 'patch':
                target = grid((3.5, -.45), TEAL_C, columns=2, total=4)
                self.play(ReplacementTransform(left, target), run_time=duration)
                content.add(target)
            else:
                self.play(ReplacementTransform(left, right), run_time=duration)
            self.wait(.12)
            old = content
            write_progress(index + 1, len(rows))
        self.wait(max(.5, 7.5-len(rows)*(duration+.12)))
