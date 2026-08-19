class ApplicationError(Exception):
    """Error controlado y apto para mostrar al usuario."""


class ValidationError(ApplicationError):
    """Los datos ingresados no superan las validaciones."""


class NotFoundError(ApplicationError):
    """El registro solicitado no existe."""


class ConflictError(ApplicationError):
    """La operación produce un conflicto con datos existentes."""


class BusinessRuleError(ApplicationError):
    """La operación vulnera una regla funcional."""