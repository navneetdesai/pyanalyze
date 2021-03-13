# static analysis: ignore
from .test_name_check_visitor import TestNameCheckVisitorBase
from .test_node_visitor import assert_fails, assert_passes, skip_before
from .error_code import ErrorCode
from .value import KnownValue, TypedValue, UNRESOLVED_VALUE


class TestProperty(TestNameCheckVisitorBase):
    @assert_passes()
    def test_property(self):
        from pyanalyze.tests import PropertyObject

        def capybara(uid):
            assert_is_value(PropertyObject(uid).string_property, TypedValue(str))


class TestShadowing(TestNameCheckVisitorBase):
    @assert_passes()
    def test(self):
        def shadow_them(locals, __import__, *list, **dict):
            return (
                [int for int in list] * locals + __import__ + [v for v in dict.values()]
            )

        shadow_them(5, [1, 2], 3)


class TestCalls(TestNameCheckVisitorBase):
    @assert_fails(ErrorCode.incompatible_call)
    def test_too_few_args(self):
        def fn(x, y):
            return x + y

        def run():
            fn(1)

    @assert_passes()
    def test_correct_args(self):
        def fn(x, y):
            return x + y

        def run():
            fn(1, 2)

    @assert_fails(ErrorCode.incompatible_call)
    def test_wrong_kwarg(self):
        def fn(x, y=3):
            return x + y

        def run():
            fn(1, z=2)

    @assert_passes()
    def test_right_kwarg(self):
        def fn(x, y=3):
            return x + y

        def run():
            fn(1, y=2)

    @assert_passes()
    def test_classmethod_arg(self):
        class Capybara(object):
            @classmethod
            def hutia(cls):
                pass

            def tucotuco(self):
                self.hutia()

    @assert_passes()
    def test_staticmethod_arg(self):
        class Capybara(object):
            @staticmethod
            def hutia():
                pass

            def tucotuco(self):
                self.hutia()

    @assert_fails(ErrorCode.incompatible_call)
    def test_staticmethod_bad_arg(self):
        class Capybara(object):
            @staticmethod
            def hutia():
                pass

            def tucotuco(self):
                self.hutia(1)

    @assert_fails(ErrorCode.not_callable)
    def test_typ_call(self):
        def run(elts):
            lst = [x for x in elts]
            assert_is_value(lst, TypedValue(list))
            lst()

    @assert_passes()
    def test_override__call__(self):
        class WithCall(object):
            def __call__(self, arg):
                return arg * 2

        def capybara(x):
            obj = WithCall()
            assert_is_value(obj, TypedValue(WithCall))
            assert_is_value(obj(x), UNRESOLVED_VALUE)

    @assert_fails(ErrorCode.incompatible_call)
    def test_unbound_method(self):
        class Capybara(object):
            def hutia(self, x=None):
                pass

            def tucotuco(self):
                self.hutia(y=2)

    @assert_fails(ErrorCode.undefined_attribute)
    def test_method_is_attribute(self):
        class Capybara(object):
            def __init__(self):
                self.tabs = self.tabs()

            def tabs(self):
                return []

            def hutia(self):
                self.tabs.append("hutia")

    @assert_passes()
    def test_type_inference_for_type_call(self):
        def fn():
            capybara = int("3")
            assert_is_value(capybara, TypedValue(int))

    @assert_passes()
    def test_return_value(self):
        def capybara(x):
            l = hasattr(x, "foo")
            assert_is_value(l, TypedValue(bool))

    @assert_passes()
    def test_required_kwonly_args(self):
        from pyanalyze.tests import takes_kwonly_argument

        def run():
            takes_kwonly_argument(1, kwonly_arg=True)

    @assert_fails(ErrorCode.incompatible_call)
    def test_missing_kwonly_arg(self):
        from pyanalyze.tests import takes_kwonly_argument

        def run():
            takes_kwonly_argument(1)

    @assert_fails(ErrorCode.incompatible_argument)
    def test_wrong_type_kwonly_arg(self):
        from pyanalyze.tests import takes_kwonly_argument

        def run():
            takes_kwonly_argument(1, kwonly_arg="capybara")

    @assert_fails(ErrorCode.incompatible_argument)
    def test_wrong_variable_name_value(self):
        def fn(qid):
            pass

        uid = 1
        fn(uid)

    @assert_fails(ErrorCode.incompatible_argument)
    def test_wrong_variable_name_value_in_attr(self):
        def fn(qid):
            pass

        class Capybara(object):
            def __init__(self, uid):
                self.uid = uid

            def get_it(self):
                return fn(self.uid)

    @assert_fails(ErrorCode.incompatible_argument)
    def test_wrong_variable_name_value_in_subscript(self):
        def fn(qid):
            pass

        def render_item(self, item):
            return fn(item["uid"])

    @assert_passes()
    def test_kwargs(self):
        def fn(**kwargs):
            pass

        fn(uid=3)

    @assert_fails(ErrorCode.incompatible_argument)
    def test_known_argspec(self):
        def run():
            getattr(False, 42)

    @assert_fails(ErrorCode.incompatible_argument)
    def test_wrong_getattr_args(self):
        def run(attr):
            getattr(False, int(attr))

    @assert_passes()
    def test_kwonly_args(self):
        from pyanalyze.tests import KeywordOnlyArguments

        def capybara():
            return KeywordOnlyArguments(kwonly_arg="hydrochoerus")

    @assert_fails(ErrorCode.incompatible_call)
    def test_kwonly_args_subclass(self):
        from pyanalyze.tests import KeywordOnlyArguments

        class Capybara(KeywordOnlyArguments):
            def __init__(self):
                pass

        def run():
            Capybara(1)

    @assert_fails(ErrorCode.incompatible_call)
    def test_kwonly_args_bad_kwarg(self):
        from pyanalyze.tests import KeywordOnlyArguments

        class Capybara(KeywordOnlyArguments):
            def __init__(self):
                pass

        def run():
            Capybara(bad_kwarg="1")

    @assert_passes()
    def test_hasattr(self):
        class Quemisia(object):
            def gravis(self):
                if hasattr(self, "xaymaca"):
                    print(self.xaymaca)

    @assert_fails(ErrorCode.incompatible_call)
    def test_hasattr_wrong_args(self):
        def run():
            hasattr()

    @assert_fails(ErrorCode.incompatible_argument)
    def test_hasattr_mistyped_args(self):
        def run():
            hasattr(True, False)

    @assert_fails(ErrorCode.incompatible_call)
    def test_keyword_only_args(self):
        from pyanalyze.tests import KeywordOnlyArguments

        class Capybara(KeywordOnlyArguments):
            def __init__(self, neochoerus):
                pass

        def run():
            Capybara(hydrochoerus=None)

    @assert_passes()
    def test_correct_keyword_only_args(self):
        from pyanalyze.tests import KeywordOnlyArguments

        class Capybara(KeywordOnlyArguments):
            def __init__(self, neochoerus):
                pass

        def run():
            # This fails at runtime, but pyanalyze accepts it because of a special case
            # in pyanalyze.test_config.TestConfig.CLASS_TO_KEYWORD_ONLY_ARGUMENTS.
            Capybara(None, kwonly_arg="capybara")

    @assert_fails(ErrorCode.undefined_name)
    def test_undefined_args(self):
        def fn():
            return fn(*x)

    @assert_fails(ErrorCode.undefined_name)
    def test_undefined_kwargs(self):
        def fn():
            return fn(**x)


class TestTypeVar(TestNameCheckVisitorBase):
    @assert_passes()
    def test_simple(self):
        from typing import TypeVar, List, Generic

        T = TypeVar("T")

        def id(obj: T) -> T:
            return obj

        def get_one(obj: List[T]) -> T:
            for elt in obj:
                return elt
            assert False

        class GenCls(Generic[T]):
            def get_one(self: "GenCls[T]") -> T:
                raise NotImplementedError

            def get_another(self) -> T:
                raise NotImplementedError

        def capybara(x: str, xs: List[int], gen: GenCls[int]) -> None:
            assert_is_value(id(3), KnownValue(3))
            assert_is_value(id(x), TypedValue(str))
            assert_is_value(get_one(xs), TypedValue(int))
            assert_is_value(get_one([int(3)]), TypedValue(int))
            # This one doesn't work yet because we don't know how to go from
            # KnownValue([3]) to a GenericValue of some sort.
            # assert_is_value(get_one([3]), KnownValue(3))

            assert_is_value(gen.get_one(), TypedValue(int))
            assert_is_value(gen.get_another(), TypedValue(int))

    @assert_fails(ErrorCode.incompatible_argument)
    def test_only_T(self):
        from typing import Generic, TypeVar

        T = TypeVar("T")

        class Capybara(Generic[T]):
            def add_one(self, obj: T) -> None:
                pass

        def capybara(x: Capybara[int]) -> None:
            x.add_one("x")

    @assert_passes()
    def test_multi_typevar(self):
        from typing import TypeVar, Optional

        T = TypeVar("T")

        # inspired by tempfile.mktemp
        def mktemp(prefix: Optional[T] = None, suffix: Optional[T] = None) -> T:
            raise NotImplementedError

        def capybara() -> None:
            assert_is_value(mktemp(), UNRESOLVED_VALUE)
            assert_is_value(mktemp(prefix="p"), KnownValue("p"))
            assert_is_value(mktemp(suffix="s"), KnownValue("s"))

    @assert_passes()
    def test_generic_base(self):
        from typing import TypeVar, Generic

        T = TypeVar("T")

        class Base(Generic[T]):
            pass

        class Derived(Base[int]):
            pass

        def take_base(b: Base[int]) -> None:
            pass

        def capybara(c: Derived):
            take_base(c)

    @assert_fails(ErrorCode.incompatible_argument)
    def test_wrong_generic_base(self):
        from typing import TypeVar, Generic

        T = TypeVar("T")

        class Base(Generic[T]):
            pass

        class Derived(Base[int]):
            pass

        def take_base(b: Base[str]) -> None:
            pass

        def capybara(c: Derived):
            take_base(c)

    @skip_before((3, 10))
    @assert_fails(ErrorCode.incompatible_argument)
    def test_typeshed(self):
        from typing import List

        def capybara(lst: List[int]) -> None:
            lst.append("x")

    @assert_passes()
    def test_generic_super(self):
        from typing import Generic, TypeVar

        T = TypeVar("T")

        class A(Generic[T]):
            def capybara(self) -> None:
                pass

        class B(A):
            def capybara(self) -> None:
                super().capybara()