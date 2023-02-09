from flask import Flask, render_template, request#,flash, request
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
from keras.models import load_model
import requests
import numpy as np
#import extractFeatures
import phosutil
from keras import backend as K
import tensorflow as tf
 
# App config.

app = Flask(__name__)
app.config.from_object(__name__)
app.debug = True
#DEBUG = True
#app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/cite')
def cite():
    return render_template('cite.html', title='Citation')

@app.route('/supl')
def supl():
    return render_template('supl.html', title='Supplementary Data')

@app.route('/about')
def about():
    return render_template('about.html', title='About us')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
 
class PredForm(Form):
    sequence = TextAreaField(u'Protien Sequence &nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp(Enter A Fasta \
        format Sequence or Just Sequence Text)', [validators.DataRequired()])

def SimpleFastaParser(fasta_sequence):
    seq = fasta_sequence.split('\n')
    seq = seq[1:]
    re = ''
    for x in seq:
        re = re + x[:len(x)-2]
    return re

def SimpleParser(sequence):
    seq = sequence.split('\n')
    re = ''
    for x in seq:
        re = re + x[:len(x)-2]
    return re

@app.route("/pred", methods=['GET', 'POST'])
def pred():
    form = PredForm(request.form)
    print (form.errors)
    if request.method == 'POST':
        input_seq = request.form['sequence']
        sequence = ''
        if '>' in input_seq:
            sequence = SimpleFastaParser(input_seq)
        else:
            sequence = SimpleParser(input_seq)
        sample_list, idx_list = phosutil.samplesfromProtein("S", sequence)
        sess = tf.Session()
        K.set_session(sess)
        try:
            cnn_model = load_model("cnnPhosphos.h5")
        except Exception as e:
            #pass
            raise e
        #result = "Who let the dogs out"
        X = np.array([phosutil.encode_sample(a) for a in sample_list])
        y = cnn_model.predict_classes(X)
        sess.close()
        tmp= np.nonzero(y)[0]
        pos_site_list = [idx_list[a] for a in tmp]
        pos_seq_list = [sample_list[a] for a in tmp]
        result = dict(zip(pos_site_list, pos_seq_list))
        #result = extractFeatures.extractFeatures.formatSeq(sequence)
        return resultPage(result)
        #return resultPage(pos_seq_list, pos_site_list)
    
    return render_template('pred.html', form=form, title="Prediction" )

def resultPage(result):
    return render_template('sznresult.html', result=result, title="Results")


if __name__ == "__main__":
    #app.run("6000",debug=True)
    app.run(host="127.0.0.1", port=32000, debug=True)