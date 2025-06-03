from ..models.detection import Detection
from ..extensions import db
from datetime import datetime
from decimal import Decimal

class IngestionService:
    @staticmethod
    def store_detection(data):
        try:
            new_detection = Detection(
                latitude=Decimal(data.get('latitude')),
                longitude=Decimal(data.get('longitude')),
                detection_count=data.get('detection_count', 1),
                detection_timestamp=datetime.fromisoformat(data.get('detection_timestamp')) if data.get('detection_timestamp') else datetime.utcnow(),
                environmental_context=data.get('environmental_context'),
                risk_assessment=data.get('risk_assessment'),
                source=data.get('source')
            )
            db.session.add(new_detection)
            db.session.commit()
            return new_detection.to_dict(), 201
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 400

    @staticmethod
    def get_all_detections(args):
        query = Detection.query
        
        # Example filtering (can be expanded)
        start_time = args.get('start_time')
        end_time = args.get('end_time')

        if start_time:
            query = query.filter(Detection.detection_timestamp >= datetime.fromisoformat(start_time))
        if end_time:
            query = query.filter(Detection.detection_timestamp <= datetime.fromisoformat(end_time))
            
        detections = query.order_by(Detection.detection_timestamp.desc()).all()
        return [d.to_dict() for d in detections], 200

    @staticmethod
    def get_detection_by_id(detection_id):
        detection = Detection.query.get(detection_id)
        if detection:
            return detection.to_dict(), 200
        return {'error': 'Detection not found'}, 404
