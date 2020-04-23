import os, csv, requests

from flask import Flask, session, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import requests
# from goodreads_api_client import gr

api_key = '0AdlIaUBdaEdIoMUGaDnQg'
api_secret = 'FWRqW6uznpmpoDpk2JoOZIj5c4y5Ym6oNrWYOFC5A'

# request.response(https://www.goodreads.com/book/review_counts.json?key={api_key}&isbns=0596009208,0596517742)

def isbn(i):
    i = [i]
    response = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key":api_key,"isbns":i})
    print(response)

isbn('0804177996')



