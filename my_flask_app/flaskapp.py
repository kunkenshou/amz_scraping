from flask import Flask, render_template
import boto3

app = Flask(__name__)

@app.route("/")
def index():
    dynamodb = boto3.resource('dynamodb', region_name='ap-northeast-1')
    table = dynamodb.Table('AmzScraping')
    response = table.scan()
    items = response['Items']
    return render_template('index.html', items=items)

if __name__ == "__main__":
    app.run(debug=True)
    app.run(host='0.0.0.0')
