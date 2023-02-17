from flask import Flask, render_template, request, jsonify
from flask_cors import CORS, cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import logging
import csv
logging.basicConfig(filename="log_file/scrapper.log" , level=logging.INFO)

logging.info('#####################app start##########################')


app = Flask(__name__)

@app.route("/", methods = ['GET'])
def homepage():
    logging.info('home_page hit by machine:{}'.format(request.remote_addr))
    return render_template("index.html")
    

@app.route("/review", methods = ['GET','POST'])
def index():
    if request.method == 'POST':
        try:
            ###########scarpping code start############
            serachstring= request.form['content'].replace(" ","")
            flipkart_url = "https://www.flipkart.com/search?q=" + serachstring
            uClient= uReq(flipkart_url)
            flipkart_source_code=uClient.read()
            uClient.close()
            flipkart_html=bs(flipkart_source_code, "html.parser")
            big_box=flipkart_html.findAll("div", {"class": "_1AtVbE col-12-12"})
            small_box="https://www.flipkart.com" + big_box[2].div.div.div.a["href"]
            serached_prod= uReq(small_box)
            prod_code=serached_prod.read()
            serached_prod.close()
            prod_code_bs=bs(prod_code,"html.parser")
            review_code=prod_code_bs.findAll("div", {"class": "_16PBlm"})
            ############end###########
            logging.info('review_code ready with length : {} '.format(len(review_code)))
            review_file= []

            for i in review_code:
                try:
                    review_text=i.div.div.findAll("div", {"class" : "t-ZTKy"})[0].text
                except Exception as e:
                    logging.error(e)

            
                try:
                    review_rating=i.div.div.findAll("div" , {"class" : "_3LWZlK _1BLPMq"})[0].text
                except :
                    review_rating ='No Rating'
                    logging.info('no rating found')

            
                try:
                    review_cust_name=i.div.div.find_all('p', {'class': '_2sc7ZR _2V5EHH'})[0].text 
                except Exception as e:
                    logging.error(e)

                try:
                    review_head=i.div.div.div.p.text
                except:
                    review_head='No comment head found'
                    logging.info('no comment head found')

                mydict = {"Product": serachstring, "Name": review_cust_name, "Rating": review_rating, "CommentHead": review_head,
                          "Comment": review_text}
                review_file.append(mydict)

                logging.info('mydict append completed')

            filename= serachstring + ".csv"
            with open('search_hist/'+filename, 'w', encoding ="utf-8",newline='') as file:
                writer = csv.DictWriter(file, fieldnames=review_file[0].keys())
                writer.writeheader()

                # write each dictionary in the list to a new row in the CSV file
                for d in review_file:
                    writer.writerow(d)



            print(serachstring)
            return render_template('result.html', reviews=review_file[0:(len(review_file)-1)])

        except Exception as e:
            logging.critical(e)
            return 'Somthings fishy, contact devloper or burger off'             
        
if __name__=="__main__":
    app.run(host="0.0.0.0")
