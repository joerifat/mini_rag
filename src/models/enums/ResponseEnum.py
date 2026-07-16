from enum import Enum

class UserResponses(Enum):
    
    FILE_VALIDATED_SUCCESS = "file_validate_successfully"
    FILE_TYPE_NOT_SUPPORTED = "file_type_not_supported"
    FILE_SIZE_EXCEEDED = "file_size_exceeded"
    FILE_UPLOAD_SUCCESS = "file_upload_success"
    FILE_UPLOAD_FAILED = "file_upload_failed"
    PROCESSING_FAILED= "processing_failed"
    PROCESSING_SUCCESS="processing_successed"
    FILE_ID_ERROR_VALUE="No such file with this ID"
    NO_FILES_ERROR = "not_found_files"

