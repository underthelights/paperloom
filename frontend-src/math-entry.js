import renderMathInElement from 'katex/contrib/auto-render';
window.paperloomMath=el=>renderMathInElement(el,{delimiters:[{left:'$$',right:'$$',display:true},{left:'$',right:'$',display:false}],throwOnError:false,trust:false,strict:'ignore'});
