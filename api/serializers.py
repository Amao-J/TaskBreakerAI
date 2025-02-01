from rest_framework import serializers
from .models import User, Preferences, Goals, Subtasks,Team,Invitation

class InvitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invitation
        fields = '__all__'



class SubtaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subtasks
        fields = ['id', 'description', 'completed', 'created_at', 'end_time', 'completed_at', 'priority']

class GoalSerializer(serializers.ModelSerializer):
    subtasks = SubtaskSerializer(many=True, read_only=True)

    class Meta:
        model = Goals
        fields = ['id', 'description', 'completed', 'created_at', 'due_date', 'subtasks']




class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'password', 'password_confirm']
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def validate(self, attrs):
    
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Passwords must match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')

        
        user = User.objects.create_user(
            email=validated_data['email'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        user.set_password(password)
        user.save()

        return user

class PreferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Preferences
        fields = ['id','roles','sound','time_of_day','task_management']
        
        
        
        
class TeamSerializer(serializers.ModelSerializer):
    creator = serializers.ReadOnlyField(source='creator.id')

    class Meta:
        model = Team
        fields = ['id', 'name', 'size', 'workspace_details', 'creator', 'members', 'created_at']