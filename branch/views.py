from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from electronic_queue.firestore import db
from branch.serializers import BranchInFirestoreSerializer


BRANCH_COLLECTION_ID = "branches"


class BranchInFirestoreDetailView(APIView):
    def get(self, request, branch_id):
        branch = db.collection(BRANCH_COLLECTION_ID).document(branch_id).get()

        if branch.exists:
            return Response(branch.to_dict(), status=status.HTTP_200_OK)
        else:
            return Response("Provided ID didn't match any branch!", status=status.HTTP_406_NOT_ACCEPTABLE)

    def post(self, request, branch_id):
        ...


class BranchInFirestoreListCreateView(APIView):
    def post(self, request):
        data = request.data
        serializer = BranchInFirestoreSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        branch_id = serializer.data.get("branch_id")
        branch_ref = db.collection(BRANCH_COLLECTION_ID).document(branch_id)
        branch_ref.set(serializer.data)
        return Response(branch_ref.get().to_dict(), status=status.HTTP_200_OK)
