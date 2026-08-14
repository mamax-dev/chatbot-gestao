const form=document.querySelector('#form');
const input=document.querySelector('#question');
const send=document.querySelector('#send');
const chat=document.querySelector('#chat');
const launcher=document.querySelector('#chat-launcher');
const win=document.querySelector('#chat-window');
const closeBtn=document.querySelector('#chat-close');
const formError=document.querySelector('#form-error');
function toggleChat(open){win.classList.toggle('open',open);win.setAttribute('aria-hidden',String(!open));launcher.setAttribute('aria-expanded',String(open));launcher.hidden=open;if(open)setTimeout(()=>input.focus(),80)}
launcher.addEventListener('click',()=>toggleChat(true));
closeBtn.addEventListener('click',()=>toggleChat(false));
document.querySelectorAll('[data-open-chat]').forEach(el=>el.addEventListener('click',()=>toggleChat(true)));
function addMessage(text,type,evidence='',cached=false){const item=document.createElement('article');item.className=`message ${type}`;const body=document.createElement('div');body.textContent=text;item.appendChild(body);if(type==='bot'&&evidence){const details=document.createElement('details');details.className='source-details';const summary=document.createElement('summary');summary.textContent='Ver fonte documental';const source=document.createElement('p');source.textContent=evidence;details.append(summary,source);item.appendChild(details)}if(type==='bot'&&cached){const badge=document.createElement('small');badge.className='cached-badge';badge.textContent='Resposta reutilizada para agilizar o atendimento.';item.appendChild(badge)}chat.appendChild(item);chat.scrollTop=chat.scrollHeight;return item}
function friendlyError(data,status){if(status===422){const detail=Array.isArray(data?.detail)?data.detail[0]:null;if(detail?.type==='string_too_short')return 'Digite uma pergunta com pelo menos 2 caracteres.';if(detail?.type==='string_too_long')return 'A pergunta deve ter no máximo 500 caracteres.';return 'Revise a pergunta e tente novamente.'}if(typeof data?.detail==='string')return data.detail;return 'Não foi possível concluir o atendimento. Tente novamente.'}
async function ask(question){const clean=question.trim();formError.hidden=true;if(clean.length<2){formError.textContent='Digite uma pergunta com pelo menos 2 caracteres.';formError.hidden=false;input.focus();return}addMessage(clean,'user');input.value='';send.disabled=true;const waiting=addMessage('Consultando as informações…','bot');try{const response=await fetch('/api/perguntar',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({question:clean})});const data=await response.json().catch(()=>({}));waiting.remove();if(response.ok)addMessage(data.answer||'Não foi possível responder.','bot',data.evidence||'',Boolean(data.cached));else addMessage(friendlyError(data,response.status),'bot')}catch{waiting.remove();addMessage('Não foi possível conectar ao atendimento. Tente novamente.','bot')}finally{send.disabled=false;input.focus()}}
form.addEventListener('submit',event=>{event.preventDefault();ask(input.value)});
document.querySelectorAll('[data-question]').forEach(el=>el.addEventListener('click',()=>ask(el.dataset.question)));
input.addEventListener('input',()=>{formError.hidden=true});
