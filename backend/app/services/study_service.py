from app.repositories.study_repository import DuplicateStudyError

class StudyService:
    def __init__(self, study_repository, spatial_service):
        self.study_repository = study_repository
        self.spatial_service = spatial_service

    def calculate_and_save(self, feeder, study_code, longitude, latitude):
        result = self.spatial_service.connect(feeder, longitude, latitude)
        if result is None:
            return None
        study = dict(result)
        study["study_code"] = study_code
        return self.study_repository.save(study)

    def restore(self, feeder, study_code):
        return self.study_repository.get(feeder.upper(), study_code)

    def list_for_feeder(self, feeder):
        return self.study_repository.list_for_feeder(feeder.upper())

__all__ = ["StudyService", "DuplicateStudyError"]
