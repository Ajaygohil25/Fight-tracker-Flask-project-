from flask import Flask, render_template, redirect, request,url_for
from sqlalchemy.orm import *
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime,timedelta
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
db= SQLAlchemy(app)


class User(db.Model):
    id= db.Column(db.Integer, primary_key=True)
    name= db.Column(db.String(255), nullable=False)

class Fights(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    desc = db.Column(db.String(255), nullable=False) 
    datetime= db.Column(db.DateTime, default=datetime.utcnow)
    streak = db.Column(db.Integer, default=1)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user= db.relationship('User',backref=db.backref('fights', lazy=True))
    def __init__(self, title, desc,user_id):
        self.title = title
        self.desc = desc
        self.user_id = user_id

    def __repr__(self) -> str:
        return f"{self.title} -  {self.id}"
    
with app.app_context():
    db.create_all()
   
@app.route('/', methods=['GET', 'POST'])
def function():
    user= User.query.first()
    if not user:
         user = User(name="Avi")
         db.session.add(user)
         db.session.commit()
    if request.method=='POST':
        title= request.form['title']
        desc= request.form['desc']
        # logic for streaks
        last_fight= Fights.query.filter_by(user_id=user.id).order_by(Fights.datetime.desc()).first()
        if last_fight:
            days_since_last_fight= (datetime.utcnow().date()- last_fight.datetime.date()).days
            if days_since_last_fight !=0:
                last_fight.streak= days_since_last_fight
            else:
                last_fight.streak=1    
        # add  notes
        fight= Fights(title= title, desc= desc, user_id=user.id)
        db.session.add(fight)
        db.session.commit()   
        return redirect(url_for('function'))
    

    allfights = Fights.query.all()
    streak  = [fight.streak for fight in allfights]
    max_streak= max(streak) if streak else 0
    return render_template ('index.html', allfights=allfights,max_streak=max_streak ,user=user)

@app.route('/update/<int:id>', methods=['GET','POST'])
def update(id):
    if request.method=='POST':
         title= request.form['title']
         desc= request.form['desc']
         fight = Fights.query.filter_by(id=id).first()
         fight.title= title
         fight.desc= desc
         db.session.add(fight)
         db.session.commit()
         print('Updated')   
         return redirect('/')
    
    fight = Fights.query.filter_by(id=id).first()
    return render_template('update.html', fight=fight)

@app.route('/delete/<int:id>')
def delete(id):
    obj = Fights.query.filter_by(id=id).first()
    if obj is not None:
        db.session.delete(obj)
        db.session.commit()
    return redirect(url_for('function'))

if __name__ == '__main__':
    app.run(debug=True)
