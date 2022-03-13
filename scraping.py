# Import Splinter and BeautifulSoup
from splinter import Browser
from bs4 import BeautifulSoup as soup
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import datetime as dt

def scrape_all():
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)

    news_title, news_paragraph = mars_news(browser)

    hemisphere_photos = hemisphere(browser)

    data = {
        "news_title": news_title,
        "news_paragraph":news_paragraph,
        "featured_image":featured_image(browser),
        "facts":mars_facts(),
        "last_modified":dt.datetime.now(),
        "hemisphere": hemisphere_photos
    }

    browser.quit()
    return data

def mars_news(browser):
    # Visit the mars nasa news site
    url = 'https://redplanetscience.com'
    browser.visit(url)
    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    html = browser.html
    news_soup = soup(html, 'html.parser')
    try:
        slide_elem = news_soup.select_one('div.list_text')

        slide_elem.find('div', class_='content_title')

        # Use the parent element to find the first `a` tag and save it as `news_title`
        news_title = slide_elem.find('div', class_='content_title').get_text()
        
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()
    except AttributeError:
        return None, None

    return news_title,news_p

# Featured Image Scrape
def featured_image(browser):
    # Visit URL
    url = 'https://spaceimages-mars.com'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    #
    try:
        # Find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')

    except AttributeError:
        return None
    
    # Use the base URL to create an absolute URL
    img_url = f'https://spaceimages-mars.com/{img_url_rel}'
    

    return img_url

# Scrape Table

#
def mars_facts():
    try:
        df = pd.read_html('https://galaxyfacts-mars.com')[0]
    except BaseException:
        return None
    
    df.columns=['Description', 'Mars', 'Earth']
    df.set_index('Description', inplace=True)

    return df.to_html()

if __name__ == "__main__":
    print(scrape_all())

def hemisphere(browser):
    
    url = 'https://marshemispheres.com/'

    browser.visit(url)

    # 2. Create a list to hold the images and titles.
    hemisphere_image_urls = []
    
    for hemisphere in range (4):
        browser.links.find_by_partial_text('Hemisphere')[hemisphere].click()

        html = browser.html 
        hemispheres_soup = soup(html, "html.parser")

        title = hemispheres_soup.find('h2',class_='title').text
        image = hemispheres_soup.find('li').a.get('href')

        #store results in dictionary
        hemispheres = {}
        hemispheres['image_url'] = f"https://marshemispheres.com/{image}"
        hemispheres['title'] = title
        hemisphere_image_urls.append(hemispheres)

        browser.back()
    return hemisphere_image_urls