const form=document.querySelector('#form');
const input=document.querySelector('#question');
const button=document.querySelector('#send');
const chat=document.querySelector('#chat');
const launcher=document.querySelector('#chat-launcher');
const chatWindow=document.querySelector('#chat-window');
const closeButton=document.querySelector('#chat-close');

function setChat(open){
  chatWindow.classList.toggle('open',open);
  chatWindow.setAttribute('aria-hidden',String(!open));
  launcher.setAttribute('aria-expanded',String(open));
  launcher.style.display=open?'none':'flex';
  if(open) input.focus();
}

launcher.addEventListener('click',()=>setChat(true));
closeButton.addEventListener('click',()=>setChat(false));
document.querySelectorAll('[data-open-chat]').forEach(el=>el.addEventListener('click',()=>setChat(true)));

function addMessage(text,type){
  const item=document.createElement('div');
  item.className=`message ${type}`;
  item.textContent=text;
  chat.appendChild(item);
  chat.scrollTop=chat.scrollHeight;
  return item;
}

form.addEventListener('submit',async event=>{
  event.preventDefault();
  const question=input.value.trim();
  if(!question)return;
  addMessage(question,'user');
  input.value='';
  button.disabled=true;
  const waiting=addMessage('Consultando as informações...','bot');
  try{
    const response=await fetch('/api/perguntar',{
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({question})
    });
    const data=await response.json();
    waiting.textContent=response.ok?data.answer:(data.detail||'Erro ao processar a pergunta.');
  }catch{
    waiting.textContent='Não foi possível conectar ao atendimento.';
  }finally{
    button.disabled=false;
    input.focus();
  }
});
