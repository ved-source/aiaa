from config import supabase


def save_message(
        tenant_id,
        user_id,
        role,
        content
):

    supabase.table(
        "chat_messages"
    ).insert({

        "tenant_id": tenant_id,
        "user_id": user_id,
        "role": role,
        "content": content

    }).execute()


def get_chat_history(
        tenant_id,
        user_id,
        limit=50
):

    response = (

        supabase.table(
            "chat_messages"
        )

        .select("*")

        .eq(
            "tenant_id",
            tenant_id
        )

        .eq(
            "user_id",
            user_id
        )

        .order(
            "created_at"
        )

        .limit(limit)

        .execute()

    )

    return response.data