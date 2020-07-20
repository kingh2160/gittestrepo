import sqlite3
import telegram
import datetime
from bs4 import BeautifulSoup

# Find the target string, return list
def FindStrAll( findlist, target ):
    ret = []
    for i in findlist: ret.append( i.get(target) )
    return ret

# Skip할 게시물 개수 Count
def SkipCnt( boardtype, soup ):
    if( boardtype ==  0 ): return len(soup.find_all( "tr", "top" )+soup.find_all("tr", "emBlue"))
    elif( boardtype == 1 ): return len(soup.find_all("tr", style="cursor:pointer;border-top:1px solid #dee2e6;background-color: papayawhip"))
    else: return 0

def FindTopId( boardtype ):
    con1 = sqlite3.connect("C:/Users/sunri/notice/test.db")
    cur1 = con1.cursor()
    sql1 = "select id from bottest where boardtype=? order by id desc"  # 현재 DB에 들어있는 가장 높은 ID값을 return, 없으면 None
    cur1.execute(sql1, (boardtype,))
    result = cur1.fetchone()                                            # return type: tuple
    con1.close()
    return result

def GetId( boardtype, link ):
    if( boardtype == 0 ):
        pos = link.find('id=')
        return link[pos+3:]
    elif( boardtype == 1 ): return link
    elif( boardtype == 3 ): 
        pos = link.find('detail/')
        return link[pos+7:]
        
def UpdateMsg( boardtype, title, origin, link, date, skipCnt, soup ):
    #1300808127:AAE1bi5_bLGEBRfYWJa3D9J2_SsKcpfkKmo
    bot1 = telegram.Bot(token='1241503130:AAE4OoAaUKdJ8SRRR5CHYFjPqc05slveQWo')                                    # 채팅방 봇 토근
    chat_id1 = -1001442438142                                                                                      # chat_id를 통해 해당 봇에게 메세지를 보내게 할 수 있음.

    sql2 = "insert into bottest(boardtype, title, link, date, id) values (?,?,?,?,?)"
    con2 = sqlite3.connect("C:/Users/sunri/notice/test.db")
    cur2 = con2.cursor()

    id_tail = []
    if( boardtype == 2 ):                                       # Korbit의 Id값 긁어오기
        target_id = soup.select( 'div > article' )
        id_tail = FindStrAll( target_id, 'id' )
        id_tail = list( map(lambda text: text[5:], id_tail))
    
    top_id = FindTopId( boardtype )
    for i, (A, B, C) in enumerate(zip( title, link, date )):
        if i < skipCnt: continue
        if( boardtype == 2 ):                                                                               
            if( top_id == None or str(top_id)[2:-3] < id_tail[i] ):
                bot1.sendMessage(chat_id=chat_id1, text=A.text + ' ' + B + ' ' + C )                     
                cur2.execute(sql2,(boardtype, A.text, B, C, id_tail[i]))                            
                con2.commit()
            else: break
        else:
            now_id = GetId(boardtype, B)
            if( top_id == None or str(top_id)[2:-3] < now_id ):
                if( len(C.text.strip()) <= 5 ):                           # YYYY.MM.DD 형태가 아닐 경우
                    nowtime = datetime.datetime.now().strftime('%H:%M')
                    if( C.text.strip() < nowtime ):
                        bot1.sendMessage(chat_id=chat_id1, text=A.text + ' ' + origin+B + ' ' + datetime.datetime.now().strftime("%Y.%m.%d") )
                        cur2.execute(sql2,(boardtype, A.text, origin+B, datetime.datetime.now().strftime("%Y.%m.%d"), now_id))                           
                        con2.commit()
                    else:
                        yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
                        bot1.sendMessage(chat_id=chat_id1, text=A.text + ' ' + origin+B + ' ' + yesterday.strftime('%Y.%m.%d') )
                        cur2.execute(sql2,(boardtype, A.text, origin+B, yesterday.strftime('%Y.%m.%d'), now_id ))                           
                        con2.commit()
                else:
                    bot1.sendMessage(chat_id=chat_id1, text=A.text + ' ' + origin+B + ' ' + C.text )                     
                    cur2.execute(sql2,(boardtype, A.text, origin+B, C.text, now_id))                            
                    con2.commit()
            else: break
    con2.close()