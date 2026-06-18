from rest_framework import serializers


class ReportQuerySerializer(serializers.Serializer):
    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)
    warehouse_id = serializers.UUIDField(required=False)

    def validate(self, attrs):
        date_from = attrs.get('date_from')
        date_to = attrs.get('date_to')

        if date_from and date_to and date_from > date_to:
            raise serializers.ValidationError({
                'date_from': 'date_from must be less than or equal to date_to.'
            })

        return attrs
