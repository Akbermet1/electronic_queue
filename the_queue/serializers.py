import uuid
from rest_framework import serializers

from electronic_queue.firestore import db
from branch.views import BRANCH_COLLECTION_ID


class QueueInFirebaseSerializer(serializers.Serializer):
    institution_id = serializers.CharField()
    customer_count_visible = serializers.BooleanField(read_only=True, default=False)
    customer_count = serializers.IntegerField(read_only=True, default=0)
    queue_id = serializers.SerializerMethodField()
    name = serializers.CharField()
    queue = serializers.ListField(read_only=True, default=[])
    branch_id = serializers.CharField()

    def validate_institution_id(self, institution_id):
        collection_title = "institutions"

        if db.collection(collection_title).document(institution_id).get().exists:
            return institution_id
        else:
            raise serializers.ValidationError("Invalid institution_id")
    
    def validate_branch_id(self, branch_id):
        if db.collection(BRANCH_COLLECTION_ID).document(branch_id).get().exists:
            return branch_id
        else:
            raise serializers.ValidationError("Invalid branch_id")
    
    def validate(self, validated_data):
        collection_title = "institutions"
        branch_id = validated_data.get("branch_id")
        institution_id = validated_data.get("institution_id")
    
        instituiton_snapshot = db.collection(collection_title).document(institution_id)
        if instituiton_snapshot.get().exists:
            branches_of_institutions = instituiton_snapshot.get().to_dict().get("branches")
            keys_of_branches = []
            for branch in branches_of_institutions:
                for key in branch.keys():
                    keys_of_branches.append(key)

            if branch_id in keys_of_branches:
                return validated_data
            else:
                raise serializers.ValidationError("The branch does not belong to the specified institution")
        else:
            raise serializers.ValidationError("Cannot find the institution")

    def get_queue_id(self, instance):
        number_in_line = str(uuid.uuid4())
        return number_in_line
    
    def retrieve_branch_address(self, branch_id):
        branch_ref = db.collection(BRANCH_COLLECTION_ID).document(branch_id).get()
        if branch_ref.exists:
            branch_doc = branch_ref.to_dict()
            branch_address = branch_doc.get("address")
            if branch_address is not None:
                return branch_address
        return ""
