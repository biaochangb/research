__author__ = 'bchang'

import urllib2

opener = urllib2.build_opener()
opener.addheaders.append(('User-Agent',
                          'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.10 Safari/537.11'))
opener.addheaders.append(('Cookie',
                          'v=0; thw=sea; cna=jeL3DZECNh8CAcqhOeJwdSyI; _tb_token_=e883a5e7ea659; lzstat_uv=3035837739883452834|3492151@1679806; lzstat_ss=949267500_0_1436534947_3492151|3855137542_0_1436534947_1679806; uc3=nk2=AQ3lVX4hxXYxmg%3D%3D&id2=W89Iviyi7Q9E&vt3=F8dAT%2B%2BGKm7QwAHyudw%3D&lg2=UtASsssmOIJ0bQ%3D%3D; existShop=MTQzNjYxMjIzNQ%3D%3D; lgc=biaochangb; tracknick=biaochangb; sg=b9d; mt=npy=&ci=0_1; _cc_=V32FPkk%2Fhw%3D%3D; tg=0; _l_g_=Ug%3D%3D; cookie2=1ca2c334931f09f91f79cb38ebc56575; cookie1=WqP1DihBc1LjIJtmem6M0Um%2Fz2q7GyZ686gsVZDJIfk%3D; unb=864942589; t=7865feb0eeb9876668590714a00f7f52; _nk_=biaochangb; cookie17=W89Iviyi7Q9E; x=e%3D1%26p%3D*%26s%3D0%26c%3D0%26f%3D0%26g%3D0%26t%3D0%26__ll%3D-1%26_ato%3D0; whl=-1%260%260%260; uc1=lltime=1436532936&cookie14=UoW0FJX2TOlUvw%3D%3D&existShop=false&cookie16=VT5L2FSpNgq6fDudInPRgavC%2BQ%3D%3D&cookie21=V32FPkk%2FgihF%2FS5nr3O5&tag=2&cookie15=U%2BGCWk%2F75gdr5Q%3D%3D&pas=0; isg=DDEDFC5B94843A37F65D9F5654493FC9; l=AoyMXyVteneKpnSjlj2dB3Tq3OS/FTBv'))
f = opener.open(
    "http://api-taojinbi.taobao.com/json/sign_in_everyday.htm?checkCode=null&t=1436614283001&_tb_token_=af7T6GPO4THAsu0z7eKRl1&enter_time=1436614273377&ua=084UW5TcyMNYQwiAiwQRHhBfEF8QXtHcklnMWc%3D%7CUm5Ockt1TnVJcE91S3FMcCY%3D%7CU2xMHDJ7G2AHYg8hAS8WKQcnCVU0Uj5ZJ11zJXM%3D%7CVGhXd1llXGJZYl5nWGJcZ1NsW2ZEfUdySXdDdk9zSXNGeUR6T3dZDw%3D%3D%7CVWldfS0TMwc8ASEbOxUpDFpsDSoNI3Uj%7CVmNDbUMV%7CV2NDbUMV%7CWGZGFisLNhYqEicZOQYzCTAQLBcqFzcDPgMjHyQZJAQxCjdhNw%3D%3D%7CWWVYeFYGOQI%2BBD4eSWdbYlxlXmNYbVRhXmJWIx48Aj8COgA6BzMHMw4zCDwDOW5AYFwKJHI%3D%7CWmNDEz0TMwY5BSUZIx4%2BAj8EOmw6%7CW2JCEjwSMg4wDjYWKhMuDjIJNg9ZDw%3D%3D%7CXGVFFTsVNQE0CCgUKRAwDzANMGYw%7CXWZGFjgWNgo1CysWNg83Aj5oPg%3D%3D%7CXmZGFjgWNmZZbFV1S3VBYV5iW3tFeUVlWWdff0d6LAwxET8RMQU4AjlvOQ%3D%3D%7CX2ZbZkZ7W2REeEF9XWNbYUF5TW1Xb09wUGRbe0FhWnpCYl1kRHhHEQ%3D%3D&_ksTS=1436614283003_77&callback=json")
print f.read()
line_id = 0
line_type = 0
results = self.db.query(
    'SELECT  LP.Id LineProductId,LP.SupplierLineTitle,LP.MainTitle,LP.SubTitle,LP.ShowTitle ,LPC.CityId DestinationCityId,\
     LPC.CityName DestinationCityName,LP.Days,LP.DataFlag,LP.IfDel,LP.RecomImage_Ids AS LineProductRecomImage\
     FROM [TCZiZhuYou].dbo.[ZZY_LineProduct] LP WITH(NOLOCK)\
     INNER JOIN [TCZiZhuYou].dbo.[ZZY_LineProductCity] LPC WITH(NOLOCK) ON LPC.LineProduct_Id=LP.Id AND LPC.DataFlag=1 AND LPC.IsDestination=1 \
     WHERE LP.Id=%d  AND LP.LineProductType=%d ' % (line_id, line_type))[0]
