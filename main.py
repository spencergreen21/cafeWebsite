from flask import Flask, jsonify, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import os


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.secret_key = os.environ.get('secret_key')
db = SQLAlchemy()
db.init_app(app)

TopSecretAPIKey = os.environ.get('TopSecretAPIKey')


class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


@app.route("/")
def get_all_cafes():
    # Parse filters from query parameters
    location = request.args.get('location')
    sockets = request.args.get('sockets')
    toilet = request.args.get('toilet')
    wifi = request.args.get('wifi')
    calls = request.args.get('calls')

    # Construct query based on filters
    query = Cafe.query
    if location:
        query = query.filter(Cafe.location == location)
    if sockets:
        query = query.filter(Cafe.has_sockets == True)  # Assuming 'sockets' is a boolean field
    if toilet:
        query = query.filter(Cafe.has_toilet == True)
    if wifi:
        query = query.filter(Cafe.has_wifi == True)
    if calls:
        query = query.filter(Cafe.can_take_calls == True)

    # Retrieve cafes based on filtered query
    cafes = query.order_by(Cafe.name).all()

    return render_template('cafes.html', cafes=cafes)


@app.route("/add", methods=["GET", "POST"])
def post_new_cafe():
    if request.method == "POST":
        # Check if API key is provided in the request
        api_key = request.form.get("api-key")
        if api_key != TopSecretAPIKey:
            flash("API key is wrong", "error")
            return redirect(url_for('get_all_cafes'))

        # Extract cafe data from the form
        name = request.form.get("name")
        map_url = request.form.get("map_url")
        img_url = request.form.get("img_url")
        location = request.form.get("loc")
        has_sockets = bool(request.form.get("sockets"))
        has_toilet = bool(request.form.get("toilet"))
        has_wifi = bool(request.form.get("wifi"))
        can_take_calls = bool(request.form.get("calls"))
        seats = request.form.get("seats")
        coffee_price = request.form.get("coffee_price")

        # Create a new Cafe object
        new_cafe = Cafe(
            name=name,
            map_url=map_url,
            img_url=img_url,
            location=location,
            has_sockets=has_sockets,
            has_toilet=has_toilet,
            has_wifi=has_wifi,
            can_take_calls=can_take_calls,
            seats=seats,
            coffee_price=coffee_price,
        )

        # Add the new cafe to the database
        db.session.add(new_cafe)
        db.session.commit()
        flash("Successfully added the cafe from the database.", "success")
        return redirect(url_for('get_all_cafes'))
    else:
        return render_template("add.html")


@app.route("/update-price/<int:cafe_id>", methods=["GET", "POST"])
def patch_new_price(cafe_id):
    if request.method == "POST":
        new_price = request.form.get("new_price")  # Use form instead of args
        api_key = request.form.get("api_key")
        if api_key == TopSecretAPIKey:
            cafe = Cafe.query.get_or_404(cafe_id)
            if cafe:
                cafe.coffee_price = new_price
                db.session.commit()
                flash(f"Successfully changed coffee price for {cafe.name}.", "success")
                return redirect(url_for('get_all_cafes'))
            else:
                return jsonify(error={"Not Found": "Sorry, a cafe with that id was not found in the database."}), 404
        else:
            flash("API key is wrong", "error")
            return redirect(url_for('get_all_cafes'))
    else:
        return render_template("change.html", cafe_id=cafe_id)


@app.route("/delete-cafe/<int:cafe_id>", methods=["GET", "POST"])
def delete_cafe(cafe_id):
    if request.method == "POST":
        api_key = request.form.get("api_key")
        if api_key == TopSecretAPIKey:
            cafe = Cafe.query.get_or_404(cafe_id)
            if cafe:
                db.session.delete(cafe)
                db.session.commit()
                flash(f"Successfully deleted {cafe.name} from the database.", "success")
                return redirect(url_for('get_all_cafes'))
            else:
                return jsonify(error={"Not Found": "Sorry, a cafe with that id was not found in the database."}), 404
        else:
            flash("API key is wrong", "error")
            return redirect(url_for('delete_cafe', cafe_id=cafe_id))
    else:
        return render_template("delete.html", cafe_id=cafe_id)


if __name__ == '__main__':
    app.run(debug=True)
