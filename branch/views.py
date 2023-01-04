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

    def delete(self, request, branch_id):
        branch_ref = db.collection(BRANCH_COLLECTION_ID).document(branch_id)

        if branch_ref.get().exists:
            branch_ref.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response("Provided ID didn't match any branch!", status=status.HTTP_406_NOT_ACCEPTABLE)


class BranchInFirestoreListCreateView(APIView):
    def post(self, request):
        data = request.data
        serializer = BranchInFirestoreSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        branch_id = serializer.data.get("branch_id")
        branch_ref = db.collection(BRANCH_COLLECTION_ID).document(branch_id)
        branch_ref.set(serializer.data)
        return Response(branch_ref.get().to_dict(), status=status.HTTP_200_OK)

    def get(self, reuqest):
        all_branches = db.collection(BRANCH_COLLECTION_ID).stream()
        list_of_branches = [branch.to_dict() for branch in all_branches]

        return Response(list_of_branches, status=status.HTTP_200_OK)


class BranchInFirestorePartialUpdateView(APIView):
    def post(self, request, branch_id):
        address = request.data.get("address", None)
        new_working_hours = request.data.get("new_working_hours", None)

        if address is None and new_working_hours is None:
            return Response(status=status.HTTP_204_NO_CONTENT)

        branch_ref = db.collection(BRANCH_COLLECTION_ID).document(branch_id)

        if branch_ref.get().exists:

            if address is not None:
                branch_ref.update(
                    {
                        "address": address
                    }
                )
            return Response(branch_ref.get().to_dict(), status=status.HTTP_200_OK)

        else:
            return Response("Provided ID didn't match any branch!", status=status.HTTP_406_NOT_ACCEPTABLE)
