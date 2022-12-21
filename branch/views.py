from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from electronic_queue.firestore import db


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