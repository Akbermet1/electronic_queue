import uuid

from rest_framework import serializers

from electronic_queue.firestore import db


class BranchInFirestoreSerializer(serializers.Serializer):
    institution_id = serializers.CharField()
    address = serializers.CharField()
    working_hours = serializers.SerializerMethodField()
    branch_id = serializers.SerializerMethodField()

    def validate_institution_id(self, institution_id):
        collection_title = "institutions"

        if db.collection(collection_title).document(institution_id).get().exists:
            return institution_id
        else:
            raise serializers.ValidationError("Invalid institution_id")

    def get_working_hours(self, instance):
        working_schedule = {
            "Monday": {}, 
            "Tuesday": {},
            "Wednesday": {},
            "Thursday": {},
            "Friday": {},
            "Saturday": {},
            "Sunday": {},
        }
        for key in working_schedule.keys():
            working_schedule[key] = {"from": "8:00", "till": "20:00"}
        
        return working_schedule

    def get_branch_id(self, instance):
        branch_id = str(uuid.uuid4())
        return branch_id