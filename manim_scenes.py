"""Trusted educational scenes; inputs are numeric parameters, never generated code."""
import json,os
import numpy as np
from manim import Scene,Text,VGroup,Rectangle,Line,Dot,Arrow,Create,FadeIn,FadeOut,Transform,BLUE,GREEN,YELLOW,WHITE,UP,DOWN,LEFT,RIGHT

class ConceptScene(Scene):
    def construct(self):
        self.camera.background_color='#101724'
        spec=json.load(open(os.environ['PAPERLOOM_SCENE']))
        if spec['template']=='ensemble':self.ensemble(float(spec['decay']))
        else:self.asynchronous(int(spec['latency']))

    def label(self,text,size=26):
        m=Text(text,font_size=size)
        if m.width>12:m.scale_to_fit_width(12)
        return m

    def ensemble(self,decay):
        title=self.label('Temporal ensemble: align the target time',34).to_edge(UP)
        self.play(FadeIn(title))
        subtitle=self.label('Toy example: three predictions for the SAME action time',22).next_to(title,DOWN)
        self.play(FadeIn(subtitle))
        values=np.array([0.2,0.8,0.5]);ages=np.array([2,1,0]);weights=np.exp(-decay*ages);weights/=weights.sum()
        colors=[BLUE,YELLOW,GREEN];bars=VGroup()
        for i,(a,w) in enumerate(zip(values,weights)):
            x=-4+i*4
            rect=Rectangle(width=1.4,height=max(.05,float(w)*2.5),fill_color=colors[i],fill_opacity=.8,stroke_width=0).move_to([x,-1+float(w)*1.25,0])
            lab=self.label(f'age={ages[i]}   a={a:.1f}',22).move_to([x,-1.45,0])
            weight=self.label(f'w={w:.3f}',23).next_to(rect,UP)
            bars.add(rect,lab,weight);self.play(FadeIn(VGroup(rect,lab,weight)),run_time=.6)
        formula=self.label(f'w_i = exp(-{decay:.2f} age_i) / sum_j exp(-{decay:.2f} age_j)',23).move_to([0,1.7,0]);self.play(FadeIn(formula));self.wait(1)
        result=self.label('a = '+ ' + '.join(f'{w:.3f} x {a:.1f}' for w,a in zip(weights,values))+f' = {weights@values:.3f}',27).move_to([0,-2.25,0])
        self.play(FadeIn(result));self.wait(2)
        note=self.label('This convention favors newer predictions. Verify each paper’s indexing.',20).to_edge(DOWN)
        self.play(FadeIn(note));self.wait(2)

    def asynchronous(self,latency):
        title=self.label('Asynchronous inference: computation overlaps control',32).to_edge(UP);self.play(FadeIn(title))
        self.add(self.label('Assume an initial action buffer; time is in control steps.',20).next_to(title,DOWN))
        scale=.85;origin=-3.6
        for y,name in [(1.5,'Inference'),(-.5,'Control')]:
            self.add(self.label(name,22).move_to([-5.3,y,0]));self.play(Create(Line([origin,y,0],[4.2,y,0])))
        for t in range(9):self.add(self.label(str(t),17).move_to([origin+t*scale,-1.1,0]))
        for start in (0,latency):
            end=start+latency
            if end>8:continue
            box=Rectangle(width=latency*scale,height=.5,fill_color=BLUE,fill_opacity=.8).move_to([origin+(start+latency/2)*scale,1.5,0]);self.play(FadeIn(box),run_time=.7)
            self.play(Create(Arrow([origin+end*scale,1.15,0],[origin+end*scale,-.15,0],buff=0,color=GREEN)),run_time=.5)
        cursor=Dot([origin,-.5,0],color=YELLOW);self.add(cursor)
        for t in range(1,9):self.play(cursor.animate.move_to([origin+t*scale,-.5,0]),run_time=.25)
        text=self.label(f'Inference latency: {latency} control steps; act from a buffer while computing.',23).move_to([0,-2,0]);self.play(FadeIn(text))
        self.play(FadeIn(self.label('Toy schedule only: stale observations, alignment and buffer underrun still matter.',20).to_edge(DOWN)));self.wait(3)
