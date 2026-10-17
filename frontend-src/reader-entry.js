import {marked} from 'marked';
import DOMPurify from 'dompurify';
import * as pdfjs from '../node_modules/pdfjs-dist/build/pdf.mjs';
pdfjs.GlobalWorkerOptions.workerSrc='/pdf.worker.mjs';
window.paperloomMarkdown=text=>DOMPurify.sanitize(marked.parse(text||''),{FORBID_TAGS:['img','iframe','style','form','input','video','audio'],FORBID_ATTR:['style']});
window.paperloomPdf=pdfjs;
