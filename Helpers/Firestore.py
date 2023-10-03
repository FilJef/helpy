import firebase_admin
from firebase_admin import credentials, firestore, initialize_app
from firebase_admin import db
from io import BytesIO
from google.cloud import storage
from google.cloud.firestore_v1 import FieldFilter
from google.oauth2 import service_account
from pypdf import PdfMerger
from datetime import date
import datetime as DT
import yfinance as yf

dbname = "acumulare-454db.appspot.com"
CrentialLocation = 'Key.json'


def connectFirestore():
    cred = credentials.Certificate(CrentialLocation)
    default_app = firebase_admin.initialize_app(cred)
    db = firestore.client()
    return db


def read(db, reportKey):
    reports_ref = db.collection("Reports").document("WeeklyReport")
    docs = reports_ref.get()
    print(docs.to_dict())


def write(db,data, collection, document):
    PDF_Url = data
    db.collection(collection).document(document).set({"PDF": PDF_Url,"Dist": ["UUID1","UUID2","UUID3"]})
    return


def get_report_variables(db, ref):
    today = "2023-09-25"
    doc_ref = db.collection("Distributed_Reports").document(today).collection(today+"_Send").document(ref)
    doc = doc_ref.get()
    variables = doc.to_dict()
    return variables


def get_stock_data(ticker, interval, period):
    data = yf.download(ticker, interval=interval, period=period)
    return data

def write_sub_collection(db,data, collection, document, subcollection, reportID):
    print(collection, document, subcollection, reportID)
    db.collection(collection).document(document).collection(subcollection).document(reportID).set(data)
    return


def get_TA_refs(db):
    TA_Ref = db.collection("TA_indicators")
    TA_Ref = TA_Ref.list_documents()
    doc_ids = [doc.id for doc in TA_Ref]
    return doc_ids


def get_todays_reports(db):
    today = date.today()
    collections = db.collection("Distributed_Reports").document(str(today)).collections()
    for collection in collections:
        print(collection.id)
        temp = collection.list_documents()
        doc_ids = [doc.id for doc in temp]
        print(doc_ids)


def update_next_gen(db, doc_ref, next_gen,n):
    doc_ref.update({'LastGenerated' : DT.datetime.now(), 'NextGenerated' : next_gen + DT.timedelta(days=n)})


def copy_daily_reports(db):
    #instanitate variables
    today = str(DT.date.today())
    timestamp = DT.datetime.now()
    yesterday = timestamp - DT.timedelta(days=1)
    #query db for ungenerated daily reports
    reports_ref = db.collection("Reports").where(filter=FieldFilter('NextGenerated', "<=", yesterday)).where(filter=FieldFilter('Frequency', '==', 'Daily'))
    #process response
    docs = reports_ref.get()
    doc_ids = [doc.id for doc in docs]
    #get each doc in list
    for doc_id in doc_ids:
        doc_ref = db.collection("Reports").document(doc_id)
        doc = doc_ref.get()
        data = doc.to_dict()
        #copy doc into todays generation
        write_sub_collection(db,data,"Distributed_Reports", today, today+"_Send", doc_id)
        #update next generation
        update_next_gen(db, doc_ref, data['NextGenerated'], 1)
    return doc_ids


def copy_weekly_reports(db):
    #instanitate variables
    today = str(DT.date.today())
    timestamp = DT.datetime.now()
    one_week_ago = timestamp - DT.timedelta(days=7)
    #query db for ungenerated weekly reports
    reports_ref = db.collection("Reports")\
        .where(filter=FieldFilter(('NextGenerated', "<=", one_week_ago))
        .where(filter=FieldFilter(('Frequency', '==', 'Weekly'))))
    #process response
    docs = reports_ref.get()
    doc_ids = [doc.id for doc in docs]
    #get each doc in list
    for doc_id in doc_ids:
        doc_ref = db.collection("Reports").document(doc_id)
        doc = doc_ref.get()
        data = doc.to_dict()
        #copy doc into todays generation
        write_sub_collection(db,data,"Distributed_Reports", today, today+"_Send", doc_id)
        #update next generation
        update_next_gen(db, doc_ref, data['NextGenerated'], 7)
    return doc_ids

def update_link(db, reportID, indicator, url):
    today = str(DT.date.today())
    ref = db.collection("Distributed_Reports").document(today).collection(today + "_Send").document(reportID)
    ref.update({indicator+"PDF" : url})
    return
###PDF STOREAGE###


def upload_blob(bucket_name, source_file_name, destination_blob_name):
    credentials = service_account.Credentials.from_service_account_file(CrentialLocation, scopes=['https://www.googleapis.com/auth/cloud-platform'])

    storage_client = storage.Client(credentials=credentials, project=dbname)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_name)

    print(
        f"File {source_file_name} uploaded to {destination_blob_name}."
    )
    return destination_blob_name

def download_blob(bucket_name, source_blob_name, destination_file_name):
    credentials = service_account.Credentials.from_service_account_file(CrentialLocation, scopes=['https://www.googleapis.com/auth/cloud-platform'])

    storage_client = storage.Client(credentials=credentials, project=dbname)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)

    print(
        "Downloaded storage object {} from bucket {} to local file {}.".format(
            source_blob_name, bucket_name, destination_file_name
        )
    )


def Create():
    # Instantiates a client
    credentials = service_account.Credentials.from_service_account_file(CrentialLocation, scopes=['https://www.googleapis.com/auth/cloud-platform'])

    storage_client = storage.Client(credentials=credentials, project=dbname)
    # The name for the new bucket
    bucket_name = "/temp"

    # Creates the new bucket
    bucket = storage_client.create_bucket(dbname)

    print(f"Bucket {bucket.name} created.")


def readPDF(db, reportKey):
    reports_ref = db.collection("Reports").document(reportKey)
    docs = reports_ref.get()
    doc = docs.to_dict()
    pdf = doc["PDF"]
    file_object = open("downloaded.pdf", "wb")
    b = bytes(str(pdf), 'utf-8')
    file_object.write(b)
    file_object.close()
