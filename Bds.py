from bs4 import BeautifulSoup
import lxml
import time
from selenium import webdriver
from googleapiclient.discovery import build
from google.oauth2 import service_account

# lấy dữ liệu từ 1 link 
def getData(driver,link):
    
    driver.get(link)
    res = ["Chưa xác định"]*19
    soup = BeautifulSoup(driver.page_source, "html.parser")
    # lấy các element chứa thông tin 
    title = driver.title
    basicInfomations = soup.find("ul",class_="short-detail-2 clearfix pad-16").find_all("li")
    content = soup.find("div",class_ = "des-product").text
    fullAddress = soup.find("div",class_ = "short-detail").text
    boxContact = soup.find("div",class_="box-contact")
    id = soup.find("ul",class_="short-detail-2 list2 clearfix").find_all("span")[-1].text
    Phone = boxContact.find("div",class_="phone text-center").find("span")["raw"]
    Name = boxContact.find("div",class_="name")["title"]
    boxMoreInfomations = soup.find("div",class_="box-round-grey3").find_all("div")
    boxAuth = soup.find("ul",class_="short-detail-2 list2 clearfix").find_all("li")
    Content = title.strip()+ "\n" + fullAddress.strip() + "\n" + "".join(info.text.replace(":\n",": ") for info in basicInfomations).replace("\nD","D") +"\n"*2 + "Thông tin mô tả \n" + content.strip()+"\n"*2 + "Tên liên hệ: " + Name +"\n"+ "Số điện thoại: " + Phone + "\n"*2 + "Đặc điểm bất động sản" + "".join(info.text + "\n" for info in boxMoreInfomations)+"\n"*2 + "".join(info.text + "\n" for info in boxAuth)


    if "-" in fullAddress:
        fullAddress = fullAddress.split("-")
    else:
        fullAddress = fullAddress.split(',')

    for info in boxMoreInfomations:
        # làm sạch dữ liệu rồi thêm vào result
        if "Số tầng" in info.text:
            res[13] = info.text.replace("Số tầng:","").replace(" (tầng)","")
            continue
        if "Loại tin" in info.text:
            res[7] = info.text.replace("Loại tin đăng:","")
            if "nhà" in res[7]:
                res[7] = "Nhà"
            elif "đất" in res[7]:
                res[7] = "Đất"
            

    for info in basicInfomations:
        # làm sạch dữ liệu rồi thêm vào result
        if "giá" in info.text:
            if "tỷ" in info.text.split("\n")[3]:
                res[9] = info.text.split("\n")[3].replace("~","").replace(" tỷ","")
                res[9] = int(float(res[9])*1000)
                continue
            res[9] = info.text.split("\n")[2]
            if "tỷ" in res[9]:
                res[9] = res[9].replace(" tỷ","")
                res[9] = int(float(res[9])*1000)
                continue
            elif "triệu" in res[9]:
                res[9] = res[9].replace(" triệu","")
            continue
        if "tích" in info.text:
            res[10] = info.text.split("\n")[2]
            res[10] = res[10].split(" ")[0]
            continue
        if "ngủ" in info.text:
            res[14] = info.text.replace("Phòng ngủ:","").replace(" PN","")     
    # thêm dữ liệu vào result 
    res[4] = "TP Hồ Chí Minh"
    res[5] = fullAddress[-2].strip()
    if "Thủ" in res[5] or " 9" in res[5] or " 2" in res[5]:
        res[4] = "TP Thủ Đức"
    if len(fullAddress) > 2:
        if "Phường" in fullAddress[-3] or "Xã" in fullAddress[-3] or "Thị trấn" in fullAddress[-3]: 
            res[6] = fullAddress[-3]
            
    if res[5][-1] in "198273645":
        res[5] = res[5][:-2].strip()+" 0"+res[5][-1]
    if res[6][-1] in "198273645":
        res[6] = res[6][:-2].strip()+" 0"+res[6][-1]
   
    res[0] = Content
    res[1] = link
    res[2] = "Batdongsan"
    res[3] = id
    res[15]= Phone
    res[16]= Name
    res[18]=content.strip()
    return res

    # lấy các link bài viết từ 1 page 
def getLinks(url):
    driver.get(url)
    time.sleep(1)
    soup = BeautifulSoup(driver.page_source,"html.parser")
    list_links = []
    # tìm element chứa toàn bộ link trong 1 trang 
    listLinks = soup.find("div",class_="main-left").find("div", class_ = "product-lists mar-top-16").find_all("a")
    listLinks = listLinks[:20]
    for link in listLinks: 
        list_links.append("https://batdongsan.com.vn" + link["href"]) 
    return list_links

    
# lấy tất cả các link của các trang 
def getAllLinks():
    
    listLinks = []
# Sắp xếp từ bài viết mới đến cũ  
    driver.get("https://batdongsan.com.vn/ban-nha-rieng-tp-hcm?gtn=3-ty")
    boxSort = driver.find_element_by_css_selector("body > div.form-content > div.main-container.clearfix > div.main-left > div.product-nav-bar.pad-top-8.clearfix > div > div").click()
    driver.find_element_by_css_selector("#divSortOptions > ul > li:nth-child(2)").click() 

    listLinks.append(getLinks("https://batdongsan.com.vn/ban-nha-rieng-tp-hcm?gtn=3-ty"))
    i = 1
    while True:
        i += 1
        link = "https://batdongsan.com.vn/ban-nha-rieng-tp-hcm/p" + str(i) + "?gtn=3-ty"
        # điều kiện dừng 
        listLinks.append(getLinks(link))
        if len(getLinks(link)) != 20:
            break
        if i == 10:
            break
        
    return listLinks

# lấy dữ liệu từ tất cả các link bằng hàm getData
def getAllData():
    listlinks = getAllLinks()
    driver1 = webdriver.Firefox()
    driver2 = webdriver.Firefox()
    header = ["Tin gốc đầy đủ", "Link gốc", "Nguồn gốc","ID tin nguồn","Thành phố","Quận/Huyện","Phường/Xã","Loại BĐS","Mặt tiền/Hẻm","Giá","Diện tích","Ngang","Dài","Số tầng","Số phòng ngủ", "Số điện thoại","Tên liên hệ","Link liên hệ","Tin gốc"]
    Result = [header]
    for links in listlinks:
        for i in range(0,len(links),3):
            try:
                time.sleep(0.5)
                Result.append(getData(driver,links[i]))
                time.sleep(0.5)
                Result.append(getData(driver1,links[i+1]))
                time.sleep(0.5)
                Result.append(getData(driver2,links[i+2]))
            except:
                time.sleep(1)
    return Result

def main(linkGGSheet, sheetName, startCell):
        SERVICE_ACCOUNT_FILE = 'keys.json' # đổi đường dẫn
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

        creds = None
        creds = service_account.Credentials.from_service_account_file(
                SERVICE_ACCOUNT_FILE, scopes=SCOPES)

        # id gg sheet 
        SAMPLE_SPREADSHEET_ID = linkGGSheet.split("/")[5]
        service = build('sheets', 'v4', credentials=creds)
        data_return = getAllData()
        # Call the Sheets API
        sheet = service.spreadsheets()
        result = sheet.values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                    range = sheetName + "!" + startCell, valueInputOption = 'USER_ENTERED', body = {"values":data_return}).execute()
    
if __name__ == '__main__':
    # đưa dl lên googlesheet
    driver = webdriver.Firefox()
    # main("yourLinkGGsheet","sheetname","startCell")
    main("https://docs.google.com/spreadsheets/d/13Y2VxtOJ9RA2JTZBZuAeHfAJnTc2-u2dosXDORBHwDA/edit#gid=991156574","bds_crawling","A1")
    