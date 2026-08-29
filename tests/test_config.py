from validacion_honorarios.config import settings


def test_database_name_is_configured() -> None:
    assert settings.db_name
    assert isinstance(settings.db_name, str)



def test_documents_directory_exists() -> None:
    assert settings.documents_dir.exists()
    assert settings.documents_dir.is_dir()