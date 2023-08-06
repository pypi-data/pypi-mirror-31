from django_graphql_bp.graphql.tests import constructors, cases
from django_graphql_bp.user.models import User
from graphene.test import Client


class UserTestCase(cases.OperationTestCase):
    model_class = User

    def setUp(self):
        super(UserTestCase, self).setUp()
        self.user = self.create_test_user('user', {'username': 'user'})
        self.user2 = self.create_test_user('user2', {'username': 'user2'})
        self.staff = self.create_test_user('staff', {'username': 'staff'})
        self.staff.is_staff = True
        self.staff.save()


class CreateUserTestCase(UserTestCase, cases.MutationTestCase):
    def get_mutation(self, **kwargs: dict) -> constructors.Mutation:
        return constructors.Mutation('createUser', {'ok': '', 'validationErrors': ''}, {
            'email': kwargs.get('email', self.get_user_email('createUser')),
            'password1': kwargs.get('password1', 'create_user_test_case'),
            'password2': kwargs.get('password2', 'create_user_test_case')
        })

    def test_create_user(self):
        self.create_success_test()


class UpdateUserTestCase(UserTestCase, cases.MutationTestCase):
    def get_mutation(self, **kwargs: dict) -> constructors.Mutation:
        return constructors.Mutation('updateUser', {'ok': '', 'validationErrors': ''}, {
            'name': kwargs.get('name', 'UpdateUserTestCase'),
            'pk': kwargs.get('pk', self.user.pk)
        })

    def test_update_user_by_unauthorized_user(self):
        self.update_raised_error_test(self.user, 'name', self.get_unauthorized_message())

    def test_update_user_by_not_owner(self):
        self.update_raised_error_test(
            self.user, 'name', self.get_forbidden_access_message(), self.get_context_value(self.user2))

    def test_update_user_by_owner(self):
        self.update_success_test(self.user, 'name', self.get_context_value(self.user))

    def test_update_user_by_staff(self):
        self.update_success_test(self.user, 'name', self.get_context_value(self.staff))


class DeleteUserTestCase(UserTestCase, cases.MutationTestCase):
    def get_mutation(self, **kwargs: dict) -> constructors.Mutation:
        return constructors.Mutation(
            'deleteUser', {'ok': '', 'node': {'isActive': ''}},
            {'pk': kwargs.get('pk', self.user.pk)})

    def test_delete_user_by_unauthorized_user(self):
        self.update_raised_error_test(self.user, 'is_active', self.get_unauthorized_message())

    def test_delete_user_by_not_owner(self):
        self.update_raised_error_test(
            self.user, 'is_active', self.get_forbidden_access_message(), self.get_context_value(self.user2))

    def test_delete_user_by_owner(self):
        self.update_success_test(self.user, 'is_active', self.get_context_value(self.user))

    def test_delete_user_by_staff(self):
        self.update_success_test(self.user, 'is_active', self.get_context_value(self.staff))


class LoginUserTestCase(UserTestCase, cases.MutationTestCase):
    def get_mutation(self, **kwargs: dict) -> constructors.Mutation:
        return constructors.Mutation('loginUser', {
            'node': {
                'pk': ''
            },
            'ok': ''
        }, {
            'email': kwargs.get('email', self.user.email),
            'password': kwargs.get('password', 'userpassword')
        })

    def test_log_in(self):
        result = self.get_mutation_result(self.get_context_value(), {})
        self.assert_success(result)
        self.assertEqual(self.user.pk, self.get_node_attribute_value(result, 'pk'), 'Check if user is logged in')


class LogoutUserTestCase(UserTestCase, cases.MutationTestCase):
    def get_mutation(self, **kwargs: dict) -> constructors.Mutation:
        return constructors.Mutation('logoutUser', {
            'node': {
                'pk': ''
            },
            'ok': ''
        }, {})

    def test_log_out(self):
        result = self.get_mutation_result(self.get_context_value(self.user), {})
        self.assert_success(result)
        self.assertEqual(self.user.pk, self.get_node_attribute_value(result, 'pk'), 'Check if user is logged out')


class CurrentUserTestCase(UserTestCase, cases.QueryTestCase):
    def get_query(self) -> constructors.Query:
        return constructors.Query('currentUser', {'pk': ''})

    def test_current_user_by_unauthorized_user(self):
        query = self.get_query()
        result = Client(self.get_schema()).execute(query.get_result(), context_value=self.get_context_value())
        self.assertIsNone(result['data'][query.get_name()], 'Check if user is not logged in')

    def test_current_user_by_authorized_user(self):
        query = self.get_query()
        result = Client(self.get_schema()).execute(query.get_result(), context_value=self.get_context_value(self.user))
        self.assertIsNotNone(result['data'][query.get_name()], 'Check if user is logged in')
        self.assertEqual(
            self.get_operation_field_value(result, query.get_name(), 'pk'), self.user.pk,
            'Check if logged in user is correct')


class UsersTestCase(UserTestCase, cases.QueryTestCase):
    def get_query(self) -> constructors.Query:
        return constructors.Query('users', {
            'edges': {
                'node': {
                    'pk': ''
                }
            }
        })

    def test_users_by_unauthorized_user(self):
        self.raised_error_test(self.get_forbidden_access_message())

    def test_users_by_not_staff(self):
        self.raised_error_test(self.get_forbidden_access_message(), self.get_context_value(self.user))

    def test_users_by_staff(self):
        self.collection_success_test(self.get_context_value(self.staff))
