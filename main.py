from flask import Flask, request, jsonify, abort, render_template
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///items.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    description = db.Column(db.String(200), nullable=True)

    @staticmethod
    def get_non_primary_columns():
        return [column.name for column in Contact.__table__.columns if not column.primary_key]


def make_json_response(contact: Contact) -> dict:
    return {
        'id': contact.id,
        'name': contact.name,
        'phone': contact.phone,
        'description': contact.description
    }


@app.route('/', methods=['GET'])
def root():
    return render_template('index.html'), 200


@app.route('/contacts', methods=['POST'])
def create_item():
    data = request.get_json()
    if not data:
        abort(400, 'No data provided')
    if 'name' not in data or 'phone' not in data:
        abort(400, 'Name is required')
    contact = Contact(
        name=data['name'],
        phone=data['phone'],
        description=data.get('description', '')
    )
    db.session.add(contact)
    db.session.commit()
    return jsonify(make_json_response(contact)), 201


@app.route('/contacts', methods=['GET'])
def get_all_items():
    contacts = Contact.query.all()
    return render_template(
        'contacts/index.html',
        contacts=[make_json_response(contact) for contact in contacts]
    ), 200


@app.route('/contacts/<int:item_id>', methods=['GET'])
def get_item(item_id):
    contact = Contact.query.get_or_404(item_id)
    return render_template('contacts/single.html', contact=make_json_response(contact))


@app.route('/contacts/<int:item_id>', methods=['PATCH'])
def update_item_partly(item_id):
    contact = Contact.query.get_or_404(item_id)
    data = request.get_json()
    if not data:
        abort(400, 'No data provided')
    contact_fields = Contact.get_non_primary_columns()
    if set(contact_fields) < set(data.keys()):
        abort(400, 'Invalid data provided')

    for field in data:
        setattr(contact, field, data[field])
    db.session.commit()
    return jsonify(make_json_response(contact))


@app.route('/contacts/<int:item_id>', methods=['PUT'])
def update_item_fully(item_id):
    contact = Contact.query.get_or_404(item_id)
    data = request.get_json()
    if not data:
        abort(400, 'No data provided')

    contact_fields = Contact.get_non_primary_columns()
    if set(contact_fields) != set(data.keys()):
        abort(400, 'Invalid data provided')

    for field in data:
        setattr(contact, field, data[field])
    db.session.commit()
    return jsonify(make_json_response(contact))


@app.route('/contacts/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    contact = Contact.query.get_or_404(item_id)
    db.session.delete(contact)
    db.session.commit()
    return '', 204


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=False)
