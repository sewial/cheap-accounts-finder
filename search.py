from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from bs4 import BeautifulSoup
import os

caps = DesiredCapabilities().CHROME
caps["pageLoadStrategy"] = "eager"
options = Options()
options.add_experimental_option("excludeSwitches", ["enable-logging"])
options.add_argument("--headless")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options, desired_capabilities=caps)


game = input("Game name:\n")
keywords = input("Keywords (ex: pink mercy, riot buddy, c6 xiao, eu bronze):\n")
matc = input("Should the keywords match in title exactly? (y/n)\n")
if matc != "y" and matc != "n":
    matc = "n"
stars = int(input("Minimum # of stars the seller should have (0-5):\n"))
if stars > 5:
    stars = 5
if stars < 0:
    stars = 0
total = ""
results = int(input("How many results for each website? (recommended 3):\n"))

def playerauctions(game, keywords, stars, matc, results):
    g = game.replace(" ", "-")
    k = keywords.replace(" ", "-")
    driver.get(f"https://www.playerauctions.com/{g}-account/?keyword={k}&SortField=cheapest-price")
    WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.XPATH, "/html/body/main/div/div[1]/div[2]/div[6]/div[1]")))
    #find offer table
    offers = driver.find_elements(By.XPATH, "/html/body/main/div/div[1]/div[2]/div[6]/div[1]")
    last = ""
    count = 0
    for i in offers:
        #through every offer
        offer = i.find_elements(By.CLASS_NAME, "offer-item")
        for x in offer:
            #through every element in offer
            title = x.find_element(By.CLASS_NAME, "account-title").text
            cost = x.find_element(By.CLASS_NAME, "offer-price-tag").text
            url = x.find_element(By.CLASS_NAME, "txt-hot").get_attribute("href")
            star = float(x.find_element(By.CLASS_NAME, "offer-rating").text)
            if str(cost) != last and count < results and star >= stars and check(keywords, title, matc):
                format("PLAYERAUCTIONS", title, cost, url)
                count += 1
            else:
                pass
            last = str(cost)
    print("Found playerauctions offers...")

def eldorado(game, keywords, stars, matc, results):
    g = game.replace(" ", "-")
    k = keywords.replace(" ", "%20")
    if stars == 5:
        stars = 95
    else:
        stars = stars*20
    driver.get("https://www.eldorado.gg/")
    try:
        WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.XPATH, "/html/body/eld-root/div[2]/div[2]/div/eld-home/div[2]/section/div/eld-home-featured-card[1]/div")))
        #table of available games
        games = driver.find_elements(By.XPATH, "/html/body/eld-root/eld-navbar/header/div/nav/div[1]/eld-categories-menu/div[2]/div/eld-categories-menu-dropdown[2]/div/div/div/div/eld-categories-menu-all-games/div/div/div")
        for i in games:
            #look through game table to find the matching game
            gametitles = i.find_elements(By.CLASS_NAME, "category-menu-dropdown-item")
            for x in gametitles:
                name = x.find_element(By.TAG_NAME, "a").get_attribute("href")
                if len(g) <= 7:
                    if g[:4].lower() == name[24:28].lower():
                        driver.get(f"{name}?searchQuery={k}&gamePageOfferIndex=1&gamePageOfferSize=100")
                        #game offer site
                        break
                else:
                    if g[:7].lower() == name[24:31].lower():
                        driver.get(f"{name}?searchQuery={k}&gamePageOfferIndex=1&gamePageOfferSize=100")
                        #game offer site
                        break
        WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.XPATH, "/html/body/eld-root/div[2]/div[2]/div/eld-game-page/div/section/div/eld-game-page-multi-offer/eld-game-offers/div")))
        s = driver.page_source
        soup = BeautifulSoup(s, "html.parser")
        offers = soup.find("div", class_="offers")
        cheapest = {}
        last = 100000
        offer = offers.find_all("div")
        for x in offer:
            try:
                title = x.find("div", class_="offer-title hyphenate").text
                cost = x.find("div", class_="offer-amount").text
                url = "https://www.eldorado.gg" + str(x.find("a")["href"])
                star = x.find("div", class_="seller-details").contents[1].text
                star = float(star.split("%")[0])
                c = cost.replace("$", "")
                c = c.replace(",", "")
                #add to the dict if this offer is cheaper than the last offer
                if float(c) != last and star >= stars and check(keywords, title, matc):
                    #tuple dict by price
                    cheapest[c] = (title, cost, url)
                    #organise dict to 3 of the cheapest items, compare prices
                    reduce(cheapest, results)
                    last = float(c)
            except:
                pass
        for i in cheapest:
            (t, c, u) = cheapest[i]
            format("ELDORADO", t, c, u)
        print("Found eldorado offers...")
    except:
        print("Didn't find eldorado offers...")

def igv(game, keywords, stars, matc, results, pg):
    k = keywords.replace(" ", "%20")
    if stars == 5:
        stars = 4
    driver.get(f"https://www.igv.com/c2c-index/search?key={game}%20{k}{pg}&star={stars}")
    WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.XPATH, "/html/body/section[1]/div/div/div/div[2]/div/div[3]/div[2]/ul")))
    s = driver.page_source
    soup = BeautifulSoup(s, "html.parser")
    #offer table
    offers = soup.find("ul", class_="search-pros")
    offer = offers.find_all("li")
    cheapest = {}
    last = 100000
    for x in offer:
        try:
            title = x["data-pname"]
            cost = x.find("strong", class_="cly2 f16").text
            c = cost.split(" ")[0]
            url = "https://www.igv.com/" + str(x.find("a")["href"])
            star = x.find("b", class_="clg f16").text
            star = float(star.split(" ")[0])
            if float(c) != last and star >= stars and check(keywords, title, matc):
                cheapest[c] = (title, cost, url)
                reduce(cheapest, results)
                last = float(c)
        except:
            pass
    for i in cheapest:
        (t, c, u) = cheapest[i]
        format("IGV", t, c, u)
    if pg != "&":
        print("Found igv offers...")

def g2g(game, keywords, stars, matc, results):
    g = game.replace(" ", "%20")
    k = keywords.replace(" ", "%20")
    driver.get(f"https://www.g2g.com/trending/accounts?q={g}")
    #wait for page to load
    try:
        WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.XPATH, "/html/body/div[1]/div/div[1]/main/div[4]/div[2]/div/div/div[1]/div/a/div/div[2]")))
        #find the game
        s = driver.page_source
        soup = BeautifulSoup(s, "html.parser")
        t = soup.find("div", class_="col-sm-4 col-md-3 col-12")
        games = t.find("div", class_="fit")
        driver.get("https://www.g2g.com" + str(games.find("a")["href"]) + f"?sort=lowest_price&q={k}")
        WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.XPATH, "/html/body/div[1]/div/div[1]/div[1]/div[5]/div[2]/div/div[2]/div[1]/div/a/div[1]")))
        s = driver.page_source
        soup = BeautifulSoup(s, "html.parser")
        offers = soup.find("div", class_="row q-col-gutter-sm-md q-px-sm-md")
        offer = offers.find_all("div", class_="col-xs-12 col-sm-6 col-md-3")
        cheapest = {}
        last = 100000
        for x in offer:
            try:
                title = x.find("span").text.strip()
                c = x.find("div", class_="text-body1 text-weight-medium").text.strip()
                cost = "$ " + c
                url = str(x.find("a")["href"])
                if float(c) != last and check(keywords, title, matc):
                    cheapest[c] = (title, cost, url)
                    reduce(cheapest, results)
                    last = float(c)
            except:
                pass
        for i in cheapest:
            (t, c, u) = cheapest[i]
            format("G2G", t, c, u)
        print("Found g2g offers...")
    except:
        print("Didn't find g2g offers...")

def check(k, title, matc):
    if matc == "y":
        return k.lower() in title.lower()
    else:
        return k.split(" ")[0].lower() in title.lower()

def format(brand, title, cost, url):
    global total
    listings = f"{brand} | {cost} | {title} | {url}\n"
    total += listings

def reduce(dict, results):
    if len(dict) > results:
        l = list(dict.keys())
        high = max(l)
        dict.pop(high)

def notepad(game, keywords, listings):
    folder = f"./{game}"
    if not os.path.exists(folder):
        os.makedirs(folder)
    with open(f"{folder}/{keywords}.txt", "w", encoding="utf8", errors="ignore") as f:
        f.write(listings)

print("Searching...")
playerauctions(game, keywords, stars, matc, results)
eldorado(game, keywords, stars, matc, results)
igv(game, keywords, stars, matc, results // 2, "&")
igv(game, keywords, stars, matc, -(results // -2), "&page=1")
g2g(game, keywords, stars, matc, results)
notepad(game, keywords, total)
y = total.count("\n")
print(f"Found {y} offers for {game} {keywords} with seller rating {stars}...want more offers? Lower the star rating/don't match keywords exactly/increase results")
driver.quit()
