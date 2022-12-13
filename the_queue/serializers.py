import uuid
from rest_framework import serializers

from electronic_queue.firestore import db


class QueueInFirebaseSerializer(serializers.Serializer):
    institution_id = serializers.CharField()
    customer_count_visible = serializers.BooleanField(read_only=True, default=False)
    customer_count = serializers.IntegerField(read_only=True, default=0)
    queue_id = serializers.SerializerMethodField()
    name = serializers.CharField()

    def validate_institution_id(self, institution_id):
        collection_title = "institutions"

        if db.collection(collection_title).document(institution_id).get().exists:
            return institution_id
        else:
            raise serializers.ValidationError("Invalid institution_id")

    def get_queue_id(self, instance):
        number_in_line = str(uuid.uuid4())
        return number_in_line
    
