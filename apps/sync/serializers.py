from rest_framework import serializers


class SyncOperationSerializer(serializers.Serializer):
    id = serializers.UUIDField(required=False)
    clientId = serializers.UUIDField(required=False)
    action = serializers.ChoiceField(choices=[
        'CREATE_ORDER',
        'CREATE_RECEIPT',
        'CREATE_RETURN',
        'CREATE_PAYMENT',
    ])
    payload = serializers.DictField()

    def validate(self, attrs):
        payload = attrs.get('payload') or {}

        if not attrs.get('id') and not attrs.get('clientId') and not payload.get('id') and not payload.get('clientId'):
            raise serializers.ValidationError('Operation id or clientId is required.')

        return attrs


class SyncPushSerializer(serializers.Serializer):
    operations = SyncOperationSerializer(many=True)
