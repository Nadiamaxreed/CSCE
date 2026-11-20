/** Build/server only. Not connected to pages or automatic sync. */
export interface ContentHubConfig {baseUrl:string;token:string;companyId:number;}
export interface HubCategory {id:number;company_id:number;name:string;sort_order:number;}
export interface HubNews {uuid:string;company_id:number;title:string;author:string;cover_image:string;digest:string;external_url:string;categories:{name:string}[];exhibition:{uuid:string;title:string}|null;published_at:string;created_at:string|null;updated_at:string|null;}
export interface HubPage {items:HubNews[];pagination:{page:number;per_page:number;total:number;last_page:number};}
const positive=(v:number)=>{if(!Number.isSafeInteger(v)||v<1)throw new Error('参数须为正整数');return v;};
export function createContentHubNewsApi(config:ContentHubConfig){
 const base=new URL(config.baseUrl);
 if(base.protocol!=='https:'||base.username||base.password||base.search||base.hash||base.pathname.replace(/\/$/,'')!=='/api/v1')throw new Error('须提供以/api/v1结尾的无凭据HTTPS基础地址');
 positive(config.companyId);
 if(!config.token.trim()||/[\r\n]/.test(config.token))throw new Error('须提供服务端API凭据');
 async function request<T>(path:string,params:Record<string,number>={}):Promise<T>{
  const url=new URL(base.href.replace(/\/$/,'')+'/'+path);
  url.search=new URLSearchParams(Object.entries({company_id:config.companyId,...params}).map(([k,v])=>[k,String(v)])).toString();
  const response=await fetch(url,{headers:{Authorization:`Bearer ${config.token}`,Accept:'application/json'},redirect:'error',signal:AbortSignal.timeout(15000)});
  if(!response.ok)throw new Error(`内容中台HTTP失败：${response.status}`);
  const body:unknown=await response.json();
  if(!body||typeof body!=='object'||!('code'in body)||body.code!==0||!('data'in body))throw new Error('内容中台业务失败或响应不符');
  return body.data as T;
 }
 return {
  categories:()=>request<{items:HubCategory[]}>('news-categories'),
  list:(page=1,perPage=100,categoryId?:number)=>{
   positive(page);positive(perPage);if(perPage>100)throw new Error('每页最多100条');
   const params:Record<string,number>={page,per_page:perPage};if(categoryId!==undefined)params.category_id=positive(categoryId);
   return request<HubPage>('news',params);
  },
  detail:(uuid:string)=>{
   if(!/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(uuid))throw new Error('新闻UUID格式不符');
   return request<HubNews & {content:string}>('news/'+uuid);
  }
 };
}
