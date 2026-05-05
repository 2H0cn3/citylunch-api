import logging

logger = logging.getLogger(__name__)


def notify_new_livreur(email: str, prenom: str, password: str) -> None:
    """Notifie le livreur de la création de son compte avec son mot de passe.

    En production : brancher ici un vrai service d'envoi d'email
    (SendGrid, Amazon SES, Mailgun, SMTP applicatif...).
    Pour le projet, on log + on affiche dans la console.
    """
    message = (
        "\n=== NOTIFICATION LIVREUR ===\n"
        f"Destinataire : {email}\n"
        f"Bonjour {prenom},\n"
        "Votre compte CityLunch a été créé.\n"
        f"Votre mot de passe temporaire : {password}\n"
        "Pensez à le changer dès votre première connexion.\n"
        "============================\n"
    )
    logger.info(message)
    print(message)