import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
export default defineConfig({site:'https://csce.hm-d.cn',devToolbar:{enabled:false},output:'static',trailingSlash:'always',integrations:[sitemap({filter:(url)=>!url.endsWith('/news/article/')&&!url.endsWith('/news/detail/')&&!url.endsWith('/404.html')})],server:{host:'127.0.0.1',port:4326}});
