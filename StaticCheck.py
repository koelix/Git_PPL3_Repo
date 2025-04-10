from AST import *
from Visitor import *
from Utils import Utils
from StaticError import *
from functools import reduce
from typing import List, Tuple

from StaticError import Type as StaticErrorType
from AST import Type

class FuntionType(Type):
    def __str__(self):
        return "FuntionType"

    def accept(self, v, param):
        return v.visitFuntionType(self, v, param)

class Symbol:
    def __init__(self,name,mtype,value = None):
        self.name = name
        self.mtype = mtype
        self.value = value

    def __str__(self):
        return "Symbol(" + str(self.name) + "," + str(self.mtype) + ("" if self.value is None else "," + str(self.value)) + ")"

class StaticChecker(BaseVisitor,Utils):
    def __init__(self,ast):
        self.ast = ast
        self.list_type: List[Union[StructType, InterfaceType]] = []
        self.list_function: List[FuncDecl] =  [
            FuncDecl("getInt", [], IntType(), Block([])),
            FuncDecl("putInt", [ParamDecl("VOTIEN", IntType())], VoidType(), Block([])),
            FuncDecl("putIntLn", [ParamDecl("VOTIEN", IntType())], VoidType(), Block([])),

            FuncDecl("getFloat", [], FloatType(), Block([])),
            FuncDecl("putFloat", [ParamDecl("VOTIEN", FloatType())], VoidType(), Block([])),
            FuncDecl("putFloatLn", [ParamDecl("VOTIEN", FloatType())], VoidType(), Block([])),

            FuncDecl("getBool", [], BoolType(), Block([])),
            FuncDecl("putBool", [ParamDecl("VOTIEN", BoolType())], VoidType(), Block([])),
            FuncDecl("putBoolLn", [ParamDecl("VOTIEN", BoolType())], VoidType(), Block([])),

            FuncDecl("getString", [], StringType(), Block([])),
            FuncDecl("putString", [ParamDecl("VOTIEN", StringType())], VoidType(), Block([])),
            FuncDecl("putStringLn", [ParamDecl("VOTIEN", StringType())], VoidType(), Block([])),

            FuncDecl("putLn", [], VoidType(), Block([]))
        ]
        # function_current chỉ được dùng để check trong return
        self.function_current: FuncDecl = None

    def check(self):
        self.visit(self.ast, None)

    def checkType(self, LSH_type: Type, RHS_type: Type, list_type_permission: List[Tuple[Type, Type]] = []) -> bool:
        # kiểm tra phía trái là struct và phía bên phải là nil (nil được trả về struct type với name là rỗng)
        if type(RHS_type) == StructType and RHS_type.name == "":
            return # TODO: Implement

        # chuyển kiểu id về struct/interface
        LSH_type = self.lookup(LSH_type.name, self.list_type, lambda x: x.name) if isinstance(LSH_type, Id) else LSH_type
        RHS_type = self.lookup(RHS_type.name, self.list_type, lambda x: x.name) if isinstance(RHS_type, Id) else RHS_type

        # kiểm tra các cặp cho phép có thể float = int, inteface = struct
        # Những cái này được gọi từ VarDecl, ConstDecl và Assign
        if (type(LSH_type), type(RHS_type)) in list_type_permission:
            if isinstance(LSH_type, InterfaceType) and isinstance(RHS_type, StructType):
                # nếu mà inteface = struct cần phải kiểm tra các hàm trong inface có trong struct hay không (bao gồm return, params, name)
                return # TODO: Implement
            return True

        # so sánh struct/interface
        # if # TODO: Implement:
        #     return LSH_type.name == RHS_type.name

        # so sánh array
        if isinstance(LSH_type, ArrayType) and isinstance(RHS_type, ArrayType):
            return  # TOOO với các phần tử trong dimens đều là IntLiteral (này sẽ được chuyển đổi ở bước sau)

        # so sánh kiểu bình thường
        return type(LSH_type) == type(RHS_type)

    def visitProgram(self, ast: Program,c : None):
        def visitMethodDecl(ast: MethodDecl, c: StructType) -> MethodDecl:
            pass
            # TODO: Implement

        list_str = ["getInt", "putInt", "putIntLn", "getFloat", "putFloat", "putFloatLn", "getBool", "putBool", "putBoolLn", "getString", "putString", "putStringLn", "putLn"]

        for item in ast.decl:
            if isinstance(item, Type):
                if item.name in list_str:
                    raise Redeclared(StaticErrorType(), item.name)
                list_str.append(item.name)
            # TODO

        # Lấy ra danh sách các Type sẽ gồm interface và struct
        self.list_type = reduce(lambda acc, ele: [self.visit(ele, acc)] + acc if isinstance(ele, Type) else acc, ast.decl, [])

        # lấy ra danh sách các function (ở bước này chưa cần kiểm tra tên function có lặp lại không)
        self.list_function = self.list_function + list(filter(lambda item: isinstance(item, FuncDecl), ast.decl))

        # cập nhật StructType
        list(map(
            lambda item: visitMethodDecl(item, self.lookup(item.recType.name, self.list_type, lambda x: x.name)),
             list(filter(lambda item: isinstance(item, MethodDecl), ast.decl))
        ))

        # duyệt qua các khai báo gồm method/function/var và chỉ có function/method trả về Symbol để cập vào bảng Symbol
        reduce(
            # NẾU LÀ Symbol mới được đưa vào bảng Symbol và cập nhật phần tử trả về tại trí đầu của bảng Symbol
            lambda acc, ele: [
                ([result] + acc[0]) if isinstance(result := self.visit(ele, acc), Symbol) else acc[0]
            ] + acc[1:],
            # LỌC RA method/function/var
            filter(lambda item: isinstance(item, Decl), ast.decl),
            # TẦM VỰC ĐẦU TIÊN SẼ LÀ DANH SÁCH CÁC HÀM
            [[
                Symbol("getInt", FuntionType()),
                Symbol("putInt", FuntionType()),
                Symbol("putIntLn", FuntionType()),
                Symbol("getFloat", FuntionType()),
                Symbol("putFloat", FuntionType()),
                Symbol("putFloatLn", FuntionType()),
                Symbol("getBool", FuntionType()),
                Symbol("putBool", FuntionType()),
                Symbol("putBoolLn", FuntionType()),
                Symbol("getString", FuntionType()),
                Symbol("putString", FuntionType()),
                Symbol("putStringLn", FuntionType()),
                Symbol("putLn", FuntionType())
                # TO DO: Implement - DONE
            ]]
        )

    def visitStructType(self, ast: StructType, c : List[Union[StructType, InterfaceType]]) -> StructType:
        # kiểm tra xem đã có Type nào trùng tên hay chưa để nén ra lỗi Redeclared
        res = None # TODO: Implement

        def visitElements(element: Tuple[str,Type], c: List[Tuple[str,Type]]) -> Tuple[str,Type]:
            res = self.lookup(element[0], c, lambda x: x[0])
            if not res is None:
                raise Redeclared(Field(), element[0])
            return element
            # TO DO: Implement
            # dùng để đệ quy cho elements để tìm lỗi Redeclared

        ast.elements = reduce(lambda acc,ele: [visitElements(ele,acc)] + acc , ast.elements , [])
        return ast

    def visitPrototype(self, ast: Prototype, c: List[Prototype]) -> Prototype:
        # Kiểm tra xem đã có Prototype nào trùng tên hay chưa để nén ra lỗi Redeclared
        res = self.lookup(ast.name, c, lambda x: x.name)
        if not res is None:
            raise Redeclared(Prototype(), ast.name)
        return ast
        # TO DO: Implement - Done đi tìm Redeclared Prototype của Interface

    def visitInterfaceType(self, ast: InterfaceType, c : List[Union[StructType, InterfaceType]]) -> InterfaceType:
        # Check tên của Interface xem trùng không
        res = self.lookup(ast.name, c, lambda x: x.name)
        if not res is None:
            raise Redeclared(StaticErrorType(), ast.name)
        # Check tên của từng Prototype con xem có trùng không
        ast.methods = reduce(lambda acc,ele: [self.visit(ele,acc)] + acc , ast.methods , [])
        return ast

    def visitFuncDecl(self, ast: FuncDecl, c : List[List[Symbol]]) -> Symbol:
        # kiểm tra xem Symbol có chung tên đã tồn tại trong tầm vực hiện tại hay chưa
        # TO DO: Implement - Done 0 đi tìm
        # c hay c[0] ?? Do nó nói là tầm vực hiện tại thay vì tầm vực global
        res = self.lookup(ast.name, c[0], lambda x: x.name)
        if not res is None:
            raise Redeclared(Function(), ast.name)

        # Gán function đang chạy
        self.function_current = ast

        # visit block và lấy ra danh sách param và chuyển thành Symbol trong tầm vực mới
        self.visit(ast.body, [list(reduce(lambda acc,ele: [self.visit(ele,acc)] + acc, ast.params, []))] + c)

        # Hủy gán function đang chạy
        self.function_current = None

        # trả về Symbol tương ứng với Type là FuntionType
        return Symbol(ast.name, ast.retType, None)
        # TO DO: Implement - Done Trả về Symbol của Symbol()

    def visitParamDecl(self, ast: ParamDecl, c: list[Symbol]) -> Symbol:
        # - kiểm tra xem đã có Symbol nào trùng tên hay chưa để nén ra lỗi Redeclared
        # TO DO: Implement - Done
        res = self.lookup(ast.parName, c, lambda x: x.name)
        if not res is None:
            raise Redeclared(Parameter(), ast.parName)
        return Symbol(ast.parName, ast.parType, None)

    def visitMethodDecl(self, ast: MethodDecl, c : List[List[Symbol]]) -> None:
        pass
        # TODO: Implement

    def visitVarDecl(self, ast: VarDecl, c : List[List[Symbol]]) -> Symbol:
        # Check có rùi bị trùng
        res = self.lookup(ast.varName, c[0], lambda x: x.name)
        if not res is None:
            raise Redeclared(Variable(), ast.varName)

        LHS_type = ast.varType if ast.varType else None
        RHS_type = self.visit(ast.varInit, c) if ast.varInit else None

        if RHS_type is None:
            return Symbol(ast.varName, LHS_type, None)
        elif LHS_type is None:
            return Symbol(ast.varName, RHS_type, None)
        elif self.checkType(LHS_type, RHS_type, [(FloatType, IntType), (InterfaceType, StructType)]):
            return Symbol(ast.varName, LHS_type, None)
        raise TypeMismatch(ast)

    def visitConstDecl(self, ast: ConstDecl, c : List[List[Symbol]]) -> Symbol:
        # Same logic as VarDecl, differ from VarDecl, noType is given since the Decl, so no typeCheck, need type Infer only
        # const_decl      : CONST ID ASSIGN_OP expr;
        # class ConstDecl(Decl, BlockMember):
        #     conName: str
        #     conType: Type  # None if there is no type
        #     iniExpr: Expr
        # TO DO: Implement - Done
        res = self.lookup(ast.conName, c[0], lambda x: x.name)
        if not res is None:
            raise Redeclared(Constant(), ast.conName)

        LHS_type = ast.conType if ast.conType else None
        RHS_type = self.visit(ast.iniExpr, c) if ast.iniExpr else None

        if RHS_type is None:
            return Symbol(ast.conName, LHS_type, None)
        elif LHS_type is None:
            return Symbol(ast.conName, RHS_type, None)
        elif self.checkType(LHS_type, RHS_type, [(FloatType, IntType), (InterfaceType, StructType)]):
            return Symbol(ast.conName, LHS_type, None)
        raise TypeMismatch(ast)

    def visitBlock(self, ast: Block, c: List[List[Symbol]]) -> None:
        acc = [[]] + c

        for ele in ast.member:
            result = self.visit(ele, (acc, True)) if isinstance(ele, (FuncCall, MethCall)) else self.visit(ele, acc)
            if isinstance(result, Symbol):
                acc[0] = [result] + acc[0]

    def visitForBasic(self, ast: ForBasic, c : List[List[Symbol]]) -> None:
        pass
        # if # TODO: Implement:
        #     raise TypeMismatch(ast)
        # self.visit(ast.loop, c)

    def visitForStep(self, ast: ForStep, c: List[List[Symbol]]) -> None:
        symbol = self.visit(ast.init, [[]] +  c)
        pass
        # if # TODO: Implement:
        #     raise TypeMismatch(ast)
        # self.visit(Block([ast.init] + ast.loop.member + [ast.upda]), c)

    def visitForEach(self, ast: ForEach, c: List[List[Symbol]]) -> None:
        type_array = self.visit(ast.arr, c)
        pass
        # if # TODO: Implement:
        #     raise TypeMismatch(ast)
        #
        # self.visit(Block([VarDecl(# TODO: Implement),
        #                   VarDecl(ast.value.name,
        #                           # TODO: Implement,
        #                             None)] + ast.loop.member)
        #                   , c)

    # def visitId(self, ast: Id, c: List[List[Symbol]]) -> Type:
    #     # Tìm kiếm phần tử trùng tên trong bảng Symbol
    #     res = # TODO: Implement
    #     if res and not isinstance(res.mtype, Function):
    #         return res.mtype
    #     raise Undeclared(Identifier(), ast.name)
    #
    # def visitId(self, ast: Id, c: List[List[Symbol]]) -> Type:
    #     # Tìm kiếm phần tử trùng tên trong bảng Symbol
    #     res = next(filter(None,  # TODO: Implement), None)
    #         if res and not isinstance(res.mtype, Function):
    #             # trả mtype nếu không phải kiểu Id còn kiểu id thì trả về inteface/struct
    #             return res.mtype if not isinstance(res.mtype, Id) else  # TODO: Implement
    #     raise Undeclared(Identifier(), ast.name)

    def visitId(self, ast: Id, c: list[list[Symbol]]) -> Type:
        for sublist in c:  # Iterate over all sublists in c
            res: Symbol = next(filter(lambda x: x.name == ast.name, sublist), None)
            if res and not isinstance(res.mtype, Function):
                return res.mtype if not isinstance(res.mtype, Id) else self.lookup(res.mtype.name, self.list_type, lambda x: x.name)
        raise Undeclared(Identifier(), ast.name)

    def visitFuncCall(self, ast: FuncCall, c: Union[List[List[Symbol]], Tuple[List[List[Symbol]], bool]]) -> Type:
        # 3 hàng đầu là xử lí trường hợp expr hay stmt được xử lí trong block
        is_stmt = False
        if isinstance(c, tuple):
            c, is_stmt = c

        res = self.lookup(ast.funName, self.list_function, lambda x: x.name)
        if res:
            # nếu số lượng param khác nhau
            if len(res.params) != len(ast.args):
                raise TypeMismatch(ast)
            for param, arg in zip(res.params, ast.args):
                # kiểu trả kiểu của các param có giống nhau hay không
                pass # TODO: Implement

            # nếu stmt yêu cầu type là void và nếu expr yêu cầu khác void
            # if is_stmt and # TODO: Implement:
            #     raise TypeMismatch(ast)
            # if not is_stmt # TODO: Implement:
            #     raise TypeMismatch(ast)
            return res.retType
        raise Undeclared(Function(), ast.funName)

    def visitFieldAccess(self, ast: FieldAccess, c: List[List[Symbol]]) -> Type:
        # - tìm kiếm field trong elements của structType
        receiver_type = self.visit(ast.receiver, c)
        # nếu trả về id thì cần chuyển thành struct/inteface
        # receiver_type = # TODO: Implement
        # if # TODO: Implement:
        #     raise TypeMismatch(ast)
        # receiver: Expr
        # field: str

        res = self.lookup(ast.field, receiver_type.elements, lambda x: x[0])
        if res is None:
            raise Undeclared(Field(), ast.field)
        return res[1]

    def visitMethCall(self, ast: MethCall, c: Union[List[List[Symbol]], Tuple[List[List[Symbol]], bool]]) -> Type:
        is_stmt = False
        if isinstance(c, tuple):
            c, is_stmt = c
        receiver_type = self.visit(ast.receiver, c)
        # receiver_type = # TODO: Implement
        # if # TODO: Implement:
        #     raise TypeMismatch(ast)
        res = self.lookup(ast.metName, receiver_type.methods, lambda x: x.fun.name) if isinstance(receiver_type, StructType) else self.lookup(ast.metName, receiver_type.methods, lambda x: x.name)
        if res:
            if type(receiver_type) == StructType:
                if len(res.fun.params) != len(ast.args):
                    raise TypeMismatch(ast)
                for param, arg in zip(res.fun.params, ast.args):
                    pass # TODO: Implement
                # if is_stmt and # TODO: Implement:
                #     raise TypeMismatch(ast)
                # if not is_stmt and # TODO: Implement:
                #     raise TypeMismatch(ast)
                return # TODO: Implement
            if type(receiver_type) == InterfaceType:
                if len(res.params) != len(ast.args):
                    raise TypeMismatch(ast)
                for param, arg in zip(res.params, ast.args):
                    pass
                    # if # TODO: Implement:
                    #     raise TypeMismatch(ast)

                # if is_stmt and  # TODO: Implement:
                #     raise TypeMismatch(ast)
                # if not is_stmt and # TODO: Implement:
                #     raise TypeMismatch(ast)
                return # TODO: Implement
        raise Undeclared(Method(), ast.metName)

    def visitIntType(self, ast, c: List[List[Symbol]]) -> Type: return ast
    def visitFloatType(self, ast, c: List[List[Symbol]])-> Type: return ast
    def visitBoolType(self, ast, c: List[List[Symbol]])-> Type: return ast
    def visitStringType(self, ast, c: List[List[Symbol]]) -> Type: return ast
    def visitVoidType(self, ast, c: List[List[Symbol]]) -> Type: return ast
    def visitArrayType(self, ast: ArrayType, c: List[List[Symbol]]):
        # list(map(lambda item: # TODO: Implement, ast.dimens))
        return ast

    def evaluate_ast(self, node: AST, c: List[List[Symbol]]) -> int:
        if type(node) == IntLiteral:
            return int(node.value)
        # elif type(node) == Id:
        #     res =  # TODO: TÌM GIÁ TRỊ
        #     return
        #     ## TODO binary và Unary, các trường hợp còn lại sẽ không hợp lệ vì sẽ không là kiểu int và thầy đã thông báo trên forum
        return 0

    def visitAssign(self, ast: Assign, c: List[List[Symbol]]) -> None:
        if type(ast.lhs) is Id:
            pass
            # TODO: TÌM KIẾM XEM BIẾN ĐÃ ĐƯỢC KHAI BÁO CHƯA ĐƯỢC KHAI BÁO THÌ TRẢ VỀ Symbol(ast.lhs.name, self.visit(ast.rhs, c), None)

        LHS_type = self.visit(ast.lhs, c)
        RHS_type = self.visit(ast.rhs, c)
        if not self.checkType(LHS_type, RHS_type, [(FloatType, IntType), (InterfaceType, StructType)]):
            raise TypeMismatch(ast)

    def visitIf(self, ast: If, c: List[List[Symbol]]) -> None:
        # Check kiểu của expr có phải bool không
        expr_type: Type = self.visit(ast.expr, c)
        # if # TODO: Implement - Done:
        #     raise TypeMismatch(ast)
        if not isinstance(expr_type, BoolType):
            raise TypeMismatch(ast)
        # Kiểm tra thêm các lỗi trong then, do check tuần t, ko có giá trị của expr
        self.visit(Block(ast.thenStmt.member), c)
        # Nếu có phần else, check tiếp
        if ast.elseStmt:
            self.visit(ast.elseStmt, c) # TODO: Implement - Done

    def visitContinue(self, ast, c: List[List[Symbol]]) -> None: return None
    def visitBreak(self, ast, c: List[List[Symbol]]) -> None: return None
    def visitReturn(self, ast, c: List[List[Symbol]]) -> None:
        # - so sánh type trả về với function_current (nếu không trả về mặt định vào void)
        # if not self.checkType(# TODO: Implement, self.function_current.retType):
        #     raise TypeMismatch(ast)
        return None

    def visitBinaryOp(self, ast: BinaryOp, c: List[List[Symbol]]):
        # - kiểm tra kiểu LHS và RHS trước nếu bằng nhau xét đến kiểu bên trong và type trả về
        LHS_type = self.visit(ast.left, c)
        RHS_type = self.visit(ast.right, c)

        if ast.op in ['+']:
            if self.checkType(LHS_type, RHS_type, [(IntType, FloatType), (FloatType, IntType)]):
                if type(LHS_type) == StringType:
                    return StringType()
                elif type(LHS_type) == FloatType:
                    return FloatType()
                elif type(RHS_type) == FloatType:
                    return FloatType()
                elif type(LHS_type) == IntType:
                    return IntType()
        # TODO: Implement
        raise TypeMismatch(ast)

    def visitUnaryOp(self, ast: UnaryOp, c: List[List[Symbol]]):
        unary_type = self.visit(ast.body, c)
        # TODO: Implement

    def visitArrayCell(self, ast: ArrayCell, c: List[List[Symbol]]):
        # visit đến phần tử expr
        array_type = None # TODO: Implement
        if not isinstance(array_type, ArrayType):
            raise TypeMismatch(ast)

        # if not all(map(lambda item: self.checkType(self.visit(item, c), # TODO: Implement), ast.idx)):
        #     raise TypeMismatch(ast)
        if len(array_type.dimens) == len(ast.idx):
            # trả về type khi giảm chiều (chiều 0 là type bên trong phần tử)
            return # TODO: Implement
        elif len(array_type.dimens) > len(ast.idx):
            # trả về tyep khi giảm chiều
            return # TODO: Implement
        raise TypeMismatch(ast)

    def visitIntLiteral(self, ast, c: List[List[Symbol]]) -> Type: return IntType()
    def visitFloatLiteral(self, ast, c: List[List[Symbol]]) -> Type: return FloatType()
    def visitBooleanLiteral(self, ast, c: List[List[Symbol]]) -> Type: return BoolType()
    def visitStringLiteral(self, ast, c: List[List[Symbol]]) -> Type: return StringType()
    def visitArrayLiteral(self, ast:ArrayLiteral , c: List[List[Symbol]]) -> Type:
        # 	dimens: List[Expr]
        # 	eleType: Type
        # 	value: NestedList
        def nested2recursive(dat: Union[Literal, list['NestedList']], c: List[List[Symbol]]):
            if isinstance(dat,list):
                list(map(lambda value: nested2recursive(value, c), dat))
            else:
                self.visit(dat, c)
        # nested2recursive() # TODO: Implement)
        # nested2recursive(ast.value,c) # TODO: Implement)
        return ArrayType(ast.dimens, ast.eleType)
    def visitStructLiteral(self, ast:StructLiteral, c: List[List[Symbol]]) -> Type:
        list(map(lambda value: self.visit(value[1], c), ast.elements))
        return # TODO: Implement
    def visitNilLiteral(self, ast:NilLiteral, c: List[List[Symbol]]) -> Type:
        return StructType("", [], [])