from api.models import Subtasks, Goals
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
import groq
from .serializers import SubtasksSerializer

client = groq.Client(api_key="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")

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_goal_and_generate_subtasks(request):
    description = request.data.get('description')
    if not description:
        return Response({"error": "Description is required."}, status=status.HTTP_400_BAD_REQUEST)

  
    goal = Goals.objects.create(user=request.user, description=description)

    
    try:
        llm_response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You will generate a list of subtasks for the user based on the entered task. "
                        "The subtasks should be steps that can be followed to successfully complete the task. "
                        
                    ),
                },
                {
                    "role": "user",
                    "content": description,
                },
            ],
            model="llama3-8b-8192",
        )
        subtasks = llm_response.choices[0].message.content.split("\n")
        subtasks = [subtask.strip() for subtask in subtasks if subtask.strip()]
    except Exception as e:
        return Response({"error": "Failed to generate subtasks.", "details": str(e)}, status=500)

   
    if not subtasks:
        return Response({"error": "No subtasks were generated."}, status=400)

    subtask_objects = []
    
    for subtask_description in subtasks:
        subtask = Subtasks.objects.create(
            goal=goal,
            description=subtask_description,
        )
        subtask_objects.append(subtask)

    # Prepare the response data
    response_data = {
        "goal": {
            "id": goal.id,
            "description": goal.description,
        },
        "subtasks": [
            { "description": subtask.description}
            for subtask in subtask_objects
        ],
    }

    return Response(response_data, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_subtask(request):
    serializer = SubtasksSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def edit_subtask(request, subtask_id):
    try:
        subtask = Subtasks.objects.get(id=subtask_id, goal__user=request.user)
    except Subtasks.DoesNotExist:
        return Response({'error': 'Subtask not found or you do not have permission to edit it.'}, status=status.HTTP_404_NOT_FOUND)

    serializer = SubtasksSerializer(subtask, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_goals(request):
    goals = Goals.objects.filter(user=request.user)
    response_data = []

    for goal in goals:
        subtasks = Subtasks.objects.filter(goal=goal)
        subtask_list = [{"id": subtask.id, "description": subtask.description} for subtask in subtasks]
        response_data.append({
            "goal_id": goal.id,
            "description": goal.description,
            "subtasks":subtask_list
        })

    return Response({"data": response_data})

def calendar_view(request):
    goals = Goals.objects.filter(user=request.user)
    subtasks = Subtasks.objects.filter(goal__user=request.user)

    events = []

    for goal in goals:
        events.append({
            'title': goal.description,
            'start': goal.created_at.strftime('%Y-%m-%dT%H:%M:%S'),
            'end': goal.due_date.strftime('%Y-%m-%dT%H:%M:%S') if goal.due_date else None,
            'color': 'blue',
        })

    for subtask in subtasks:
        events.append({
            'title': subtask.description,
            'start': subtask.created_at.strftime('%Y-%m-%dT%H:%M:%S'),
            'end': subtask.end_time.strftime('%Y-%m-%dT%H:%M:%S') if subtask.end_time else None,
            'color': 'green',
        })

    return JsonResponse(events, safe=False)