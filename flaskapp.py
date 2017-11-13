import os, zipfile
import sys
import pandas as pd
from werkzeug.utils import secure_filename
from flask import Flask, request, redirect, url_for, render_template, flash
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, Boolean, DateTime, String

Base = declarative_base()
allowed_extensions = set(['zip'])
app = Flask('flask_test')
app.secret_key = 'secret'
ufolder = './uploads/'
app.config['UPLOAD_FOLDER'] = ufolder

class TEST_DB(Base):
	__tablename__ = 'test_db'
	number = Column(Integer, primary_key=True, nullable=False)
	enum = Column(String(4096))
	en = Column(String(4096))
	th = Column(String(4096))
	ko = Column(String(4096))
	de = Column(String(4096))
	
def allowed_filename(filename):
	print (filename)
	return '.'in filename and \
	filename.rsplit('.', 1)[1].lower() in allowed_extensions

def insert_db(csv):
	engine = create_engine('postgresql+psycopg2://postgres:LeoLio123@localhost/postgres')
	Base.metadata.create_all(engine)
	session = sessionmaker()
	session.configure(bind=engine)
	s = session()
	for row in range(0, len(csv)):
		record = TEST_DB(**{
			'enum': csv['ENUM'][row],
			'en': csv['EN'][row],
			'th': csv['TH'][row],
			'ko': csv['KO'][row],
			'de': csv['DE'][row]
		})
		s.add(record)
	s.commit()
	s.close()

@app.route('/uploads', methods = ['GET', 'POST'])
def upload_file():
	error = None
	if request.method == 'POST':
		file = request.files['file']
		dlc_type = request.form['type']
		version = request.form['version']
		if version == None or version == '':
			error = ('Please enter a version number')
			return render_template('uploads.html', error=error)
		if file and allowed_filename(file.filename):
			filename = secure_filename(file.filename)
			if filename.endswith('.zip'):
				file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
				zip_file = zipfile.ZipFile(ufolder + filename, 'r')
				zip_file.extractall(ufolder)
				zipfile.ZipFile.close(zip_file)
				if not os.path.exists(ufolder + dlc_type + '/'):
					os.makedirs(ufolder + dlc_type + '/')
					if not os.path.exists(ufolder + dlc_type + '/' + version + '/'):
						os.makedirs(ufolder + dlc_type + '/' + version + '/')
				elif not os.path.exists(ufolder + dlc_type + '/' + version + '/'):
						os.makedirs(ufolder + dlc_type + '/' + version + '/')
				if filename.split('.')[0] + '.csv' in os.listdir(ufolder + dlc_type + '/' + version + '/'):
					error = ('Same file exists')
					return render_template('uploads.html', error=error)
				else:
					for file in os.listdir(ufolder):
						if file.endswith('.csv'):
							csv_file = file
					data = pd.read_csv(ufolder + csv_file, encoding='cp1252')															
					insert_db(data)
					data.to_csv(ufolder + dlc_type + '/' + version + '/' + filename.split('.')[0] + '.csv', index=False)
				for files in os.listdir(ufolder):
					if files.endswith('.csv') or files.endswith('.zip'):
						os.remove(ufolder + files)			
	return render_template('uploads.html')

if __name__ == '__main__':
	app.run(debug=True)