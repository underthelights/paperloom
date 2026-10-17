import {createClient} from '@supabase/supabase-js';
const app=window.paperloom;let client=null,busy=false,url='';
async function configure(){let s=(await app.api('state')).settings;if(!s.supabase_url||!s.supabase_key){client=null;return}if(client&&url===s.supabase_url)return;url=s.supabase_url;client=createClient(url,s.supabase_key,{auth:{flowType:'pkce',detectSessionInUrl:true,persistSession:true,autoRefreshToken:true}});await status()}
async function status(){let e=document.querySelector('#cloud-account');let session=client?(await client.auth.getSession()).data.session:null;if(e)e.textContent=session?'로그인됨 · '+session.user.email:'Google 계정이 연결되지 않았습니다.';return session}
async function login(){await configure();if(!client)throw Error('Supabase URL과 publishable key를 먼저 저장해주세요.');let {error}=await client.auth.signInWithOAuth({provider:'google',options:{redirectTo:location.origin+'/'}});if(error)throw error}
async function logout(){if(client)await client.auth.signOut();await status();app.toast('로그아웃했습니다. 로컬 자료는 그대로 보관됩니다.')}
async function sync(notify=false){if(busy)return;busy=true;try{await configure();let session=await status();if(!session){if(notify)throw Error('Google 로그인이 필요합니다.');return}let r=await app.api('cloud-sync',{token:session.access_token});await app.refresh();if(notify)app.toast(`클라우드 동기화 완료 · ${r.count}개 자료`)}finally{busy=false}}
window.cloud={configure,status,login,logout,sync};configure().catch(e=>app.toast(e.message,true));setInterval(()=>sync(false).catch(e=>app.toast('동기화 실패: '+e.message,true)),60000);
import {marked} from 'marked';
import DOMPurify from 'dompurify';
window.renderMarkdown=text=>DOMPurify.sanitize(marked.parse(text||''),{FORBID_TAGS:['img','iframe','style','form','input','video','audio'],FORBID_ATTR:['style']});
