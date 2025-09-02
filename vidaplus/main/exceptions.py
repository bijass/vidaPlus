from http import HTTPStatus


class ApplicationError(Exception):
    code = HTTPStatus.INTERNAL_SERVER_ERROR


class EmailAlreadyExistsError(ApplicationError):
    code = HTTPStatus.BAD_REQUEST

    def __init__(self) -> None:
        super().__init__('O email já foi cadastrado')


class AuthenticationError(ApplicationError):
    code = HTTPStatus.UNAUTHORIZED

    def __init__(self) -> None:
        super().__init__('Email ou senha inválidos')


class InvalidTokenError(ApplicationError):
    code = HTTPStatus.UNAUTHORIZED

    def __init__(self) -> None:
        super().__init__('Token inválido')


class ExpiredTokenError(ApplicationError):
    code = HTTPStatus.UNAUTHORIZED

    def __init__(self) -> None:
        super().__init__('Token expirado')


class TokenRefreshError(ApplicationError):
    code = HTTPStatus.UNAUTHORIZED

    def __init__(self) -> None:
        super().__init__('Não foi possível atualizar o token')


class PermissionRequiredError(ApplicationError):
    code = HTTPStatus.FORBIDDEN

    def __init__(self) -> None:
        super().__init__('Você não tem permissão para acessar este recurso')


class SchedulingInPastError(ApplicationError):
    code = HTTPStatus.BAD_REQUEST

    def __init__(self) -> None:
        super().__init__('Não é possível agendar no passado')


class SchedulingTimeConflictError(ApplicationError):
    code = HTTPStatus.CONFLICT

    def __init__(self) -> None:
        super().__init__('Já existe um agendamento no mesmo horário')


class UserNotFoundError(ApplicationError):
    code = HTTPStatus.NOT_FOUND

    def __init__(self) -> None:
        super().__init__('Usuário não encontrado')


class AppointmentNotFountError(ApplicationError):
    code = HTTPStatus.NOT_FOUND

    def __init__(self) -> None:
        super().__init__('Agendamento não encontrado')


class UnitNotFoundError(ApplicationError):
    code = HTTPStatus.NOT_FOUND

    def __init__(self) -> None:
        super().__init__('Unidade não encontrada')


class BedNotFoundError(ApplicationError):
    code = HTTPStatus.NOT_FOUND

    def __init__(self) -> None:
        super().__init__('Leito não encontrado')


class AdmissionNotFoundError(ApplicationError):
    code = HTTPStatus.NOT_FOUND

    def __init__(self) -> None:
        super().__init__('Internação não encontrada')


class SupplyNotFoundError(ApplicationError):
    code = HTTPStatus.NOT_FOUND

    def __init__(self) -> None:
        super().__init__('Internação não encontrada')


class BedNotAvailableError(ApplicationError):
    code = HTTPStatus.CONFLICT

    def __init__(self) -> None:
        super().__init__('Leito não disponível')
