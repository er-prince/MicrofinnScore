from flask import Flask, request, jsonify
from Savoir import Savoir
import json, time, datetime, random, binascii
from ml_helper import calculate_score
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app)

ml_host = '0.0.0.0'
ml_port = '5000'

def connect():
    with open('credentials.json') as json_data:
        credentials = json.load(json_data)
        json_data.close()
    rpcuser = credentials["rpcuser"]
    rpcpasswd = credentials["rpcpasswd"]
    rpchost = credentials["rpchost"]
    rpcport = credentials["rpcport"]
    chainname = credentials["chainname"]

    global ml_port
    ml_port = credentials["mlport"]

    return Savoir(rpcuser, rpcpasswd, rpchost, rpcport, chainname)

multichain = connect()

def send_email(subject, body,user = 'bank1.creditsense@gmail.com',pwd='daaldotarun',recipient='bank1.creditsense@gmail.com'):
    import smtplib

    FROM = user
    TO = recipient if type(recipient) is list else [recipient]
    SUBJECT = 'New Loan Applicant - Bank 1'
    TEXT = body

    # Prepare actual message
    message = """From: %s\nTo: %s\nSubject: %s\n\n%s
    """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(user, pwd)
        server.sendmail(FROM, TO, message)
        server.close()
        print('successfully sent the mail')
    except:
        print("failed to send mail")

@app.route('/')
def index():
    return 'This is the CreditSense Credit Scorer API.\n'

@app.route('/add_scored_application',methods=['POST'])
def get_credit_score():
	if request.method == 'POST':
		data = request.get_json()
		#ml model
		credit_score = calculate_score(data)
		#ml model
		data['score'] = str(credit_score)
		finaldata = json.dumps(data)

		hexval = finaldata.encode('utf-8')
		curid = datetime.datetime.now()
		multichain.publish("strm1", str(curid), binascii.hexlify(hexval))

		#send_email('A loan application has been submitted - Bank 1','User #' + str(data['id']) + ' has applied for a loan. Check credit sense portal for details and credit score.')

		return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True,host=ml_host, port=int(ml_port))
