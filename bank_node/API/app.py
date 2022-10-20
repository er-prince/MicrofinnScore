from flask import Flask, request, jsonify
from Savoir import Savoir
import requests, json, time, datetime, hashlib, sys
from random import randint
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app)

ml_host = ''
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

    global ml_host
    global ml_port
    ml_host = credentials["mlhost"]
    ml_port = credentials["mlport"]

    return Savoir(rpcuser, rpcpasswd, rpchost, rpcport, chainname)

multichain = connect()


def hash(unhashed):
    byte_id = unhashed.encode('utf-8')
    hash_object = hashlib.sha256(byte_id)
    hashed = hash_object.hexdigest()
    return hashed

def all_latest_applications():
    multichain.subscribe("strm1")
    data = multichain.liststreamitems("strm1")
    applications = {}
    for application in data:
        application = json.loads(bytearray.fromhex(application['data']).decode())
        print(application)
        if 'nodeid' in application:
            if application['nodeid'] == sys.argv[1]:
                applications[application['id']] = application
    return applications

def all_applications():
    multichain.subscribe("strm1")
    data = multichain.liststreamitems("strm1")
    applications = {}
    for application in data:
        application = json.loads(bytearray.fromhex(application['data']).decode())
        if application['id'] in applications[application['id']]:
            applications[application['id']].append(application)
        else:
            applications[application['id']] = [application]
    return applications

def get_latest_application_by_id(given_id):
    data = all_latest_applications()
    if hash(given_id) in data:
        return data[hash(given_id)]
    else:
        return None

def get_all_applications_by_id(given_id):
    hashed_id = hash(given_id)
    multichain.subscribe("strm1")
    data = multichain.liststreamitems("strm1")
    applications = []
    for application in data:
        application = json.loads(bytearray.fromhex(application['data']).decode())
        if application['id'] == hashed_id:
            applications.append(application)
    return applications
    if len(application) == 0:
        return None
    else:
        return applications

@app.route('/')
def index():
    return 'This is the CreditSense consortium.\n'

@app.route('/status',methods=['GET'])
def status():
    data = list(all_latest_applications().values())

    total_applications = len(data)
    pending_applications = 0
    approved_applications = 0
    disapproved_applications = 0

    for application in data:
        if application['status'] == 'pending':
            pending_applications += 1
        elif application['status'] == 'approved':
            approved_applications += 1
        elif application['status'] == 'disapproved':
            disapproved_applications += 1

    return jsonify({
        'total_applications':total_applications,
        'pending_applications':pending_applications,
        'approved_applications':approved_applications,
        'disapproved_applications':disapproved_applications
    })

@app.route('/get_past_data',methods=['GET'])
def get_past_data():
    bank_loan_revenue = str(randint(3000000,10000000))
    completed_applications = {'Jan':randint(200,400),
    'Feb':randint(100,300),
    'Mar':randint(100,300),
    'Apr':randint(100,300),
    'May':randint(100,300),
    'June':randint(100,300),
    'July':randint(100,300),
    'Aug':randint(100,300),
    'Sept':randint(100,300),
    'Oct':randint(100,300),
    'Nov':randint(100,300),
    'Dec':randint(100,300)}

    loan_promotion_campaign = {'Jan':randint(200,400),
    'Feb':randint(200,600),
    'Mar':randint(200,600),
    'Apr':randint(200,600),
    'May':randint(200,600),
    'June':randint(200,600),
    'July':randint(200,600),
    'Aug':randint(200,600),
    'Sept':randint(200,600),
    'Oct':randint(200,600),
    'Nov':randint(200,600),
    'Dec':randint(200,600)}

    return jsonify({'bank_loan_revenue':bank_loan_revenue,'completed_applications':completed_applications,'loan_promotion_campaign':loan_promotion_campaign})

@app.route('/all_applications',methods=['GET'])
def wrapper_all_applications():
    return jsonify(list(all_latest_applications().values()))

@app.route('/pending_applications',methods=['GET'])
def pending_applications():
    applications = list(all_latest_applications().values())
    pending_applications = []
    for application in applications:
        if application['status'] == 'pending':
            pending_applications.append(application)
    return jsonify(pending_applications)

@app.route('/add_application',methods=['POST'])
def add_application():
    old_required_fields = ['id','loan_amnt', 'funded_amnt', 'funded_amnt_inv', 'term', 'int_rate',
                'installment', 'grade', 'sub_grade', 'emp_length', 'home_ownership',
                'annual_inc', 'verification_status', 'purpose', 'dti',
                'delinq_2yrs', 'inq_last_6mths', 'open_acc', 'revol_bal', 'revol_util',
                'total_acc', 'initial_list_status', 'total_pymnt', 'total_pymnt_inv',
                'total_rec_prncp', 'total_rec_int', 'last_pymnt_amnt',
                'total_rev_hi_lim', 'loan_status_coded']
    required_fields = ['id','dti','inq_last_6mths','open_acc','emp_length_num','revol_util','grade','payment_inc_ratio','purpose','delinq_2yrs_zero','pub_rec_zero','pub_rec','short_emp','home_ownership','sub_grade_num','last_major_derog_none','last_delinq_none','delinq_2yrs']
    data = request.get_json()
    checks = [field in data for field in required_fields]
    print(checks)
    if all(checks):
        application = {}
        for field in required_fields:
            application[field] = data[field]
        application['id'] = hash(data['id'])
        application['status'] = 'pending'
        print(sys.argv[1])
        application['nodeid'] = sys.argv[1]
        print(application)
        print(ml_host + ":" + ml_port)
        r = requests.post('http://'+ml_host+':'+ml_port+'/add_scored_application', json=application)
        if (r.status_code == 200):
            return jsonify({"status":"success"})
        else:
            return jsonify({"status":"failure"})
    else:
        return jsonify({"status":"required params not provided"})

@app.route('/get_all_applications_by_id',methods=['POST'])
def wrapper_get_application_by_id():
    data = request.get_json()
    if 'id' in data:
        given_id = data['id']
        applications = get_all_applications_by_id(given_id)
        if applications is not None:
            return jsonify(applications)
        else:
            return jsonify({"status": "No such applications found."})
    else:
        return jsonify({"status": "id not provided"})

@app.route('/update_application',methods=['POST'])
def update_application():
    required_fields = ['id', 'new_status']
    data = request.get_json()
    checks = [field in data for field in required_fields]
    if all(checks):
        applicant_data = None
        hashed_id = data['id']
        applications_data = all_latest_applications()
        if hashed_id in applications_data:
            applicant_data = applications_data[hashed_id]
        #applicant_data = get_latest_application_by_id(data['id'])
        if applicant_data is not None:
            applicant_data['status'] = data['new_status']
            finaldata = json.dumps(applicant_data)

            hexval = finaldata.encode('utf-8')
            curid = datetime.datetime.now()
            multichain.publish("strm1", str(curid), hexval.hex())

            return jsonify({"status":"success"})
        else:
            return jsonify({"status":"applicant doesn't exist"})
    else:
        return jsonify({"status": "required params not provided"})

if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0', port=5000)
