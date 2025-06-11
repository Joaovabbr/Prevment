from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
CORS(app) 

app.config['SQLALCHEMY_DATABASE_URI'] = r'sqlite:///C:\Users\joaov\OneDrive - Insper - Instituto de Ensino e Pesquisa\Insper\5° semestre\InsperData\Prevment\geral\dbs_union.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class PostUnificado(db.Model):
    __tablename__ = 'posts_unificados'
    
    id = db.Column(db.Text, primary_key=True)
    entity = db.Column(db.Text)
    user = db.Column(db.Text)
    text = db.Column(db.Text)
    title = db.Column(db.Text)
    url = db.Column(db.Text)
    owner = db.Column(db.Text)
    likes = db.Column(db.Integer)
    shares = db.Column(db.Integer)
    comments = db.Column(db.Integer)
    views = db.Column(db.Integer)
    date = db.Column(db.Text)
    origem = db.Column(db.Text)
    
    def to_dict(self):
        return {
            'id': self.id,
            'entity': self.entity,
            'user': self.user,
            'text': self.text,
            'title': self.title,
            'url': self.url,
            'owner': self.owner,
            'likes': self.likes,
            'shares': self.shares,
            'comments': self.comments,
            'views': self.views,
            'date': self.date,
            'origem': self.origem
        }
    
class EntityMed(db.Model):
    __tablename__ = 'entity_med'
    
    entity = db.Column(db.TEXT, primary_key=True)
    score_med = db.Column(db.REAL)
    relat_score = db.Column(db.REAL)
    normal_score = db.Column(db.REAL)
    
    def to_dict(self):
        return {
            'entity': self.entity,
            'score_med': self.score_med,
            'relat_score': self.relat_score,
            'normal_score': self.normal_score
        }
    

@app.route('/entities', methods=['GET'])
def get_entities():
    entities = EntityMed.query.all()
    return jsonify([entity.to_dict() for entity in entities])

@app.route('/entities/<string:entity>', methods=['GET'])
def get_entity(entity):
    entity_data = EntityMed.query.get_or_404(entity)
    return jsonify(entity_data.to_dict())


if __name__ == '__main__':
    app.run(debug=True)