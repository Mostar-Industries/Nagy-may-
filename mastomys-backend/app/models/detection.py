from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from ..extensions import db

class Detection(db.Model):
    __tablename__ = 'detection_patterns' # Matches the table created earlier

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    latitude = db.Column(db.Numeric(9, 6), nullable=False)
    longitude = db.Column(db.Numeric(10, 6), nullable=False)
    detection_count = db.Column(db.Integer, default=1)
    detection_timestamp = db.Column(db.DateTime(timezone=True), nullable=False)
    environmental_context = db.Column(JSONB)
    risk_assessment = db.Column(JSONB)
    source = db.Column(db.Text)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f'<Detection {self.id} at ({self.latitude}, {self.longitude})>'

    def to_dict(self):
        return {
            'id': self.id,
            'latitude': str(self.latitude), # Convert Decimal to string for JSON
            'longitude': str(self.longitude), # Convert Decimal to string for JSON
            'detection_count': self.detection_count,
            'detection_timestamp': self.detection_timestamp.isoformat() if self.detection_timestamp else None,
            'environmental_context': self.environmental_context,
            'risk_assessment': self.risk_assessment,
            'source': self.source,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
