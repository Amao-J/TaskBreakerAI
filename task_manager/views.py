from api.models import Subtasks, Goals
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import groq
from django.utils.dateparse import parse_datetime
from django.utils.timezone import now
import logging

# Initialize logger
logger = logging.getLogger(__name__)

client = groq.Client(api_key="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")

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_goal_and_generate_subtasks(request):
    description = request.data.get('description')
    due_date_str = request.data.get('due_date')

    if not description:
        return Response({"error": "Description is required."}, status=status.HTTP_400_BAD_REQUEST)

    # Validate due_date
    due_date = None
    if due_date_str:
        try:
            due_date = parse_datetime(due_date_str)
            if due_date is None or due_date < now():
                raise ValueError("Invalid due date.")
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # Create the goal
    goal = Goals.objects.create(user=request.user, description=description, due_date=due_date)

    try:
        llm_response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You will generate a list of subtasks for the user based on the entered task. "
                        "The subtasks should be steps that can be followed to successfully complete the task. "
                        "The subtasks should not be more than 7. Do not include any formatting symbols like **."
                    ),
                },
                {"role": "user", "content": description},
            ],
            model="llama3-8b-8192",
        )
        subtasks = llm_response.choices[0].message.content.split("\n")
        subtasks = [subtask.strip() for subtask in subtasks if subtask.strip()]
    except Exception as e:
        logger.error(f"Failed to generate subtasks: {e}")
        return Response({"error": "Failed to generate subtasks.", "details": str(e)}, status=500)

    if not subtasks:
        return Response({"error": "No subtasks were generated."}, status=400)

    # Bulk create subtasks
    subtask_objects = [
        Subtasks(goal=goal, description=subtask_description)
        for subtask_description in subtasks
    ]
    Subtasks.objects.bulk_create(subtask_objects)

    # Prepare the response data
    response_data = {
        "goal": {
            "id": goal.id,
            "description": goal.description,
            "due_date": goal.due_date,
            "completed": goal.completed,
            "created_at": goal.created_at,
        },
        "subtasks": [
            {
                "id": subtask.id,
                "description": subtask.description,
                "completed": subtask.completed,
                "created_at": subtask.created_at,
            }
            for subtask in Subtasks.objects.filter(goal=goal)
        ],
    }

    return Response(response_data, status=status.HTTP_201_CREATED)
