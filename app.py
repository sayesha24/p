from flask import Flask, request, jsonify, render_template
from flask_mysqldb import MySQL
import json

app = Flask(__name__)

# Database connection settings
app.config['MYSQL_HOST'] = 'web2.revacranes.com'
app.config['MYSQL_USER'] = 'po_dbuser'
app.config['MYSQL_PASSWORD'] = 'ebwgbNaiRudPPudowrEdCNA9'
app.config['MYSQL_DB'] = 'po'

mysql = MySQL(app)

@app.route('/')
def index():
    party_email = request.args.get('partyEmail')
    if party_email:
        return render_template('form.html', party_email=party_email)
    else:
        return "Party Email is required. Please provide it as a URL parameter."

@app.route('/get-data/<vendor_email>')
def get_data(vendor_email):
    cur = mysql.connection.cursor()
    sql = """
    SELECT id, pr_no, item, remark, qty, unit, price_per_unit, delivery_period, party_remarks 
    FROM po_enquiry_sent 
    WHERE party_email = %s AND (price_per_unit IS NULL OR price_per_unit = '') AND close_st IS NULL
    """
    cur.execute(sql, [vendor_email])
    rows = cur.fetchall()
    # Convert rows to a list of dictionaries to ensure proper JSON serialization
    data = [
        {
            'id': row[0], 'pr_no': row[1], 'item': row[2], 'remark': row[3],
            'qty': row[4], 'unit': row[5], 'price_per_unit': row[6],
            'delivery_period': row[7], 'party_remarks': row[8]
        } for row in rows
    ]
    cur.close()
    return jsonify(data)

@app.route('/submit-prices', methods=['POST'])
def submit_prices():
    vendor_email = request.json['vendorEmail']
    prices = request.json['prices']
    try:
        cur = mysql.connection.cursor()
        for price_data in prices:
            sql = """
            UPDATE po_enquiry_sent SET price_per_unit = %s, delivery_period = %s, party_remarks = %s, dt_quoted = CURDATE() 
            WHERE id = %s AND party_email = %s
            """
            cur.execute(sql, (price_data['price'], price_data['deliveryPeriod'], price_data['partyRemarks'], price_data['id'], vendor_email))
        mysql.connection.commit()
        cur.close()
        return 'Prices updated successfully.'
    except Exception as e:
        return 'Error updating prices: ' + str(e), 400

if __name__ == '__main__':
    app.run(debug=True)
