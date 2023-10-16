from typing import Optional
from electronic_queue.firestore import db
from the_queue.views import INSTITUTIONS_COLLECTION_ID, QUEUES_COLLECTION_ID



def confirm_queue_owner(queue_id, institution_email: Optional[str] = None, institution_login: Optional[str] = None):
    owner_matched =  False

    queue_ref = db.collection(QUEUES_COLLECTION_ID).document(queue_id).get()
    if queue_ref.exists:
        queue_doc = queue_ref.to_dict()
        institution_id = queue_doc.get("institution_id")
        
        institution_ref = db.collection(INSTITUTIONS_COLLECTION_ID).document(institution_id).get()
        if institution_ref.exists:
            institution_doc = institution_ref.to_dict()
            if institution_email is not None:
                institution_doc_email = institution_doc.get("email")
                owner_matched = True if institution_doc_email == institution_email else False
            
            if institution_login is not None:
                institution_doc_login = institution_doc.get("login")
                owner_matched = True if institution_doc_login == institution_login else False

    return owner_matched