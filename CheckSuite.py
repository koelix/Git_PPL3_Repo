import unittest
from TestUtils import TestChecker
from AST import *
import inspect

class CheckSuite(unittest.TestCase):
    def test_001(self):
        """
var VoTien = 1;
var VoTien = 2;
        """
        input = Program([VarDecl("VoTien", None,IntLiteral(1)),VarDecl("VoTien", None,IntLiteral(2))])
        self.assertTrue(TestChecker.test(input, "Redeclared Variable: VoTien", inspect.stack()[0].function))

    def test_002(self):
        """
var VoTien = 1; 
const VoTien = 2;
        """
        input = Program([VarDecl("VoTien", None,IntLiteral(1)),ConstDecl("VoTien",None,IntLiteral(2))])
        self.assertTrue(TestChecker.test(input, "Redeclared Constant: VoTien", inspect.stack()[0].function))

    def test_003(self):
        """
const VoTien = 1; 
var VoTien = 2;
        """
        input = Program([ConstDecl("VoTien",None,IntLiteral(1)),VarDecl("VoTien", None,IntLiteral(2))])
        self.assertTrue(TestChecker.test(input, "Redeclared Variable: VoTien", inspect.stack()[0].function))

    def test_004(self):
        """
const VoTien = 1; 
func VoTien () {return;}
        """
        input = Program([ConstDecl("VoTien",None,IntLiteral(1)),FuncDecl("VoTien",[],VoidType(),Block([Return(None)]))])
        self.assertTrue(TestChecker.test(input, "Redeclared Function: VoTien", inspect.stack()[0].function))

    def test_005(self):
        """ 
func VoTien () {return;}
var VoTien = 1;
        """
        input = Program([FuncDecl("VoTien",[],VoidType(),Block([Return(None)])),VarDecl("VoTien", None,IntLiteral(1))])
        self.assertTrue(TestChecker.test(input, "Redeclared Variable: VoTien", inspect.stack()[0].function))

    def test_006(self):
        """ 
var getInt = 1;
        """
        input = Program([VarDecl("getInt", None,IntLiteral(1))])
        self.assertTrue(TestChecker.test(input, "Redeclared Variable: getInt", inspect.stack()[0].function))

    def test_007(self):
        """ 
type DANH struct {
    Votien int;
}
type DUY struct {
    Votien string;
    TIEN int;
    TIEN float;
}
        """
        input = Program([
            StructType("DANH",[("Votien",IntType())],[]),
            StructType("DUY",
                       [("Votien",StringType()),
                        ("TIEN",IntType()),
                        ("TIEN",FloatType())],[]
                       )
        ])
        self.assertTrue(TestChecker.test(input, "Redeclared Field: TIEN", inspect.stack()[0].function))

    def test_008(self):
        """ 
func (v TIEN) putIntLn () {return;}
func (v TIEN) getInt () {return;}
func (v TIEN) getInt () {return;}
type TIEN struct {
    Votien int;
}
        """
        input = Program([
            MethodDecl("v",Id("TIEN"),FuncDecl("putIntLn",[],VoidType(),Block([Return(None)]))),
            MethodDecl("v",Id("TIEN"),FuncDecl("getInt",[],VoidType(),Block([Return(None)]))),
            MethodDecl("v",Id("TIEN"),FuncDecl("getInt",[],VoidType(),Block([Return(None)]))),
            StructType("TIEN",[("Votien",IntType())],[])]
        )
        self.assertTrue(TestChecker.test(input, "Redeclared Method: getInt", inspect.stack()[0].function))

    def test_009(self):
        """ 
type VoTien interface {
    VoTien ();
    VoTien (a int);
}
        """
        input = Program([
            InterfaceType("VoTien",[Prototype("VoTien",[],VoidType()),Prototype("VoTien",[IntType()],VoidType())])]
        )
        self.assertTrue(TestChecker.test(input, "Redeclared Prototype: VoTien", inspect.stack()[0].function))

    def test_010(self):
        """ 
func Votien (a, a int) {return;}
        """
        input = Program([FuncDecl("Votien",[ParamDecl("a",IntType()),ParamDecl("a",IntType())],VoidType(),Block([Return(None)]))])
        self.assertTrue(TestChecker.test(input, "Redeclared Parameter: a", inspect.stack()[0].function))

    def test_011(self):
        """ 
func Votien (b int) {
    var b = 1;
    var a = 1;
    const a = 1;
}
        """
        input = Program(
            [
                FuncDecl("Votien",[ParamDecl("b",IntType())],VoidType(),
                         Block(
                             [VarDecl("b", None,IntLiteral(1)),
                              VarDecl("a", None,IntLiteral(1)),
                              ConstDecl("a",None,IntLiteral(1))
                              ])
                         )])
        self.assertTrue(TestChecker.test(input, "Redeclared Constant: a", inspect.stack()[0].function))

    def test_012(self):
        """ 
func Votien (b int) {
    for var a = 1; a < 1; a += 1 {
        const a = 2;
    }
}
        """
        input = Program([FuncDecl("Votien",[ParamDecl("b",IntType())],VoidType(),Block([
            ForStep(VarDecl("a", None,IntLiteral(1)),
                    BinaryOp("<", Id("a"), IntLiteral(1)),
                    Assign(Id("a"),BinaryOp("+", Id("a"), IntLiteral(1))),Block([
                ConstDecl("a",None,IntLiteral(2))]))]))])
        self.assertTrue(TestChecker.test(input, "Redeclared Constant: a", inspect.stack()[0].function))

    def test_013(self):
        """
var a = 1;
var b = a;
var c = d;
        """
        input = Program([
            VarDecl("a", None,IntLiteral(1)),
            VarDecl("b", None,Id("a")),
            VarDecl("c", None,Id("d"))]
        );
        self.assertTrue(TestChecker.test(input, "Undeclared Identifier: d", inspect.stack()[0].function))

    def test_014(self):
        """
func Votien () int {return 1;}

func foo () {
    var b = Votien();
    foo_votine();
    return;
}
        """
        input = Program([
            FuncDecl("Votien",[],IntType(),
                     Block([Return(IntLiteral(1))])),
            FuncDecl("foo",[],VoidType(),
                Block(
                    [
                        VarDecl("b", None,FuncCall("Votien",[])),
                        FuncCall("foo_votine",[]),Return(None)
                    ]
                    )
                )
                ]
        );
        self.assertTrue(TestChecker.test(input, "Undeclared Function: foo_votine", inspect.stack()[0].function))

    def test_015(self):
        """
type TIEN struct {
    Votien int;
}

func (v TIEN) getInt () {
    const c = v.Votien;
    var d = v.tien;
}
        """
        input = Program(
            [StructType("TIEN",[("Votien",IntType())],[]),
             MethodDecl("v",Id("TIEN"),
            FuncDecl("getInt",[],VoidType(),
                     Block([
                         ConstDecl("c",None,FieldAccess(Id("v"),"Votien")),
                         VarDecl("d", None,FieldAccess(Id("v"),"tien"))])
                     )
            )]
        )
        self.assertTrue(TestChecker.test(input, "Undeclared Field: tien", inspect.stack()[0].function))

    def test_016(self):
        """
type TIEN struct {
    Votien int;
}

func (v TIEN) getInt () {
    v.getInt ();
    v.putInt ();
}
        """
        input = Program(
            [StructType("TIEN",[("Votien",IntType())],[]),
             MethodDecl("v",Id("TIEN"),FuncDecl("getInt",[],VoidType(),Block(
                 [MethCall(Id("v"),"getInt",[]),
                  MethCall(Id("v"),"putInt",[])
                  ]))
                    )])
        self.assertTrue(TestChecker.test(input, "Undeclared Method: putInt", inspect.stack()[0].function))

    def test_017(self):
        """
type TIEN struct {Votien int;}
type TIEN struct {v int;}
        """
        input = Program([
            StructType("TIEN",[("Votien",IntType())],[]),
            StructType("TIEN",[("v",IntType())],[])]
        )
        self.assertTrue(TestChecker.test(input, "Redeclared Type: TIEN", inspect.stack()[0].function))

    def test_018(self):
        """
const a = 2
func foo () {
    const a = 1;
    for var a = 1; a < 1; b += 2 {
        const b = 1;
    }
}
        """
        input = Program([
            ConstDecl("a",None,IntLiteral(2)),
            FuncDecl("foo",[],VoidType(),Block([
                ConstDecl("a",None,IntLiteral(1)),
                ForStep(VarDecl("a", None,IntLiteral(1)),
                        BinaryOp("<", Id("a"), IntLiteral(1)),
                        Assign(Id("b"),BinaryOp("+=", Id("b"), IntLiteral(2))),Block([
                    ConstDecl("b",None,IntLiteral(1))]))
            ]))])
        self.assertTrue(TestChecker.test(input, "Undeclared Identifier: b", inspect.stack()[0].function))

    def test_019(self):
        """
        type TIEN struct {a [2] int;}
        type VO interface {foo() int;}

        func (v TIEN) foo() int {return 1;}

        func foo() TIEN {
            return TIEN{a: [1, 2]};
            }

            func coco() TIEN {
                VO a = foo();
                return a;
            }
        :return:
        """
        input = Program([
            StructType("TIEN",[("a",ArrayType([IntLiteral(2)],IntType()))],[]),
            InterfaceType("VO",[Prototype("foo",[],IntType())]),
            MethodDecl("v",Id("TIEN"),FuncDecl("foo",[],IntType(),Block([Return(IntLiteral(1))]))),
            FuncDecl("foo",[],Id("TIEN"),Block([
                Return(StructLiteral("TIEN",[("a",ArrayLiteral([IntLiteral(2)],IntType(),[IntLiteral(1),IntLiteral(2)]))]))
            ])),
            FuncDecl("coco",[],Id("TIEN"),Block([
                VarDecl("a",Id("VO"),FuncCall("foo",[])),
                Return(Id("a"))
            ]))
        ])
        self.assertTrue(TestChecker.test(input, "Type Mismatch: Return(Id(a))", inspect.stack()[0].function))

    def test_028(self):
        """
type TIEN interface {
    foo();
}
func TIEN() {return;}
func foo() {return;}
func TIEN() {return;}
        :return:
        """
        input = Program([
            InterfaceType("TIEN",[Prototype("foo",[],VoidType())]),
            FuncDecl("TIEN",[],VoidType(),Block([Return(None)])),
            FuncDecl("foo",[],VoidType(),Block([Return(None)])),
            FuncDecl("TIEN",[],VoidType(),Block([Return(None)]))])

    def test_032(self):
        """
func getString() {return;}
        """
        input = Program([FuncDecl("getString",[],VoidType(),Block([Return(None)]))])
        self.assertTrue(TestChecker.test(input, "Redeclared Function: getString", inspect.stack()[0].function))

    def test_041(self):
        """
type S1 struct {votien int;}
type I1 interface {votien();}

func (s S1) votien() {return;}

var b [2] S1;
var a [2] I1 = b;
        :return:
        """
        input = Program([
            StructType("S1",[("votien",IntType())],[]),
            InterfaceType("I1",[Prototype("votien",[],VoidType())]),
            MethodDecl("s",Id("S1"),FuncDecl("votien",[],VoidType(),Block([Return(None)]))),
            VarDecl("b",ArrayType([IntLiteral(2)],Id("S1")), None),
            VarDecl("a",ArrayType([IntLiteral(2)],Id("I1")),Id("b"))])
        self.assertTrue(TestChecker.test(input, "Type Mismatch: VarDecl(a,ArrayType(Id(I1),[IntLiteral(2)]),Id(b))", inspect.stack()[0].function))

    def test_044(self):
        """
type TIEN struct {
    Votien int;
}
func (v TIEN) foo (v int) {return;}
func foo () {return;}
        """
        input = Program([
            StructType("TIEN",[("Votien",IntType())],[]),
            MethodDecl("v",Id("TIEN"),FuncDecl("foo",[ParamDecl("v",IntType())],VoidType(),
                                               Block([Return(None)]))),
            FuncDecl("foo",[],VoidType(),Block([
                Return(None)]))])
        self.assertTrue(TestChecker.test(input, "VOTIEN", inspect.stack()[0].function))

    def test_051(self):
        """
const a = 2;
func foo () {
    const a = 1;
    for var a = 1; a < 1; b := 2 {
        const b = 1;
        """
        input = Program([
            ConstDecl("a",None,IntLiteral(2)),
            FuncDecl("foo",[],VoidType(),Block([
                ConstDecl("a",None,IntLiteral(1)),
                ForStep(VarDecl("a", None,IntLiteral(1)),BinaryOp("<", Id("a"), IntLiteral(1)),Assign(Id("b"),IntLiteral(2)),Block([
                    ConstDecl("b",None,IntLiteral(1))]))
            ]))])
        self.assertTrue(TestChecker.test(input, "Redeclared Constant: b", inspect.stack()[0].function))

    def test_053(self):
        """
func foo () {
    var a = 1;
    var b = 1;
    for a, b := range [3]int {1, 2, 3} {
        var b = 1;
    }
}
        :return:
        """
        input = Program([FuncDecl("foo",[],VoidType(),Block([
            VarDecl("a", None,IntLiteral(1)),
            VarDecl("b", None,IntLiteral(1)),
            ForEach(Id("a"),Id("b"),ArrayLiteral([IntLiteral(3)],IntType(),[IntLiteral(1),IntLiteral(2),IntLiteral(3)]),Block([
                VarDecl("b", None,IntLiteral(1))]))]))])
        self.assertTrue(TestChecker.test(input, "VOTIEN", inspect.stack()[0].function))

    def test_057(self):
        """
var a = 1;
func foo () {
    const b = 1;
    var c = 2;
    for a, c := range [3]int{1, 2, 3} {
        var d = e;
    }
    var d = b;
    var a = 1;
}
var d = a;
        :return:
        """
        input = Program([
            VarDecl("a", None,IntLiteral(1)),
            FuncDecl("foo",[],VoidType(),Block([
                ConstDecl("b",None,IntLiteral(1)),
                VarDecl("c", None,IntLiteral(2)),
                ForEach(Id("a"),Id("c"),ArrayLiteral([IntLiteral(3)],IntType(),[IntLiteral(1),IntLiteral(2),IntLiteral(3)]),Block([
                    VarDecl("d", None,Id("e"))])),
                VarDecl("d", None,Id("b")),
                VarDecl("a", None,IntLiteral(1))])),
            VarDecl("d", None,Id("a"))])
        self.assertTrue(TestChecker.test(input, "Undeclared Identifier: e", inspect.stack()[0].function))

    def test_061(self):
        """
var a = foo();
func foo () int {
    var a =  koo();
    var c = getInt();
    putInt(c);
    putIntLn(c);
    return 1;
}
var d = foo();
func koo () int {
    var a =  foo ();
    return 1;
}

        :return:
        """
        input = Program([
            VarDecl("a", None,FuncCall("foo",[])),
            FuncDecl("foo",[],IntType(),Block([
                VarDecl("a", None,FuncCall("koo",[])),
                VarDecl("c", None,FuncCall("getInt",[])),
                FuncCall("putInt",[Id("c")]),
                FuncCall("putIntLn",[Id("c")]),
                Return(IntLiteral(1))])),
            VarDecl("d", None,FuncCall("foo",[])),
            FuncDecl("koo",[],IntType(),Block([
                VarDecl("a", None,FuncCall("foo",[])),
                Return(IntLiteral(1))]))])
        self.assertTrue(TestChecker.test(input, "VOTIEN", inspect.stack()[0].function))

    def test_071(self):
        """
var v TIEN;
type TIEN struct {
    a int;
}
type VO interface {
    foo() int;
}

func (v TIEN) foo() int {return 1;}
func (b TIEN) koo() {b.koo();}
func foo() {
    var x VO;
    const b = x.foo();
    x.koo();
}
        """
        input = Program([
            VarDecl("v",Id("TIEN"), None),
            StructType("TIEN",[("a",IntType())],[]),
            InterfaceType("VO",[Prototype("foo",[],IntType())]),
            MethodDecl("v",Id("TIEN"),FuncDecl("foo",[],IntType(),Block([Return(IntLiteral(1))]))),
            MethodDecl("b",Id("TIEN"),FuncDecl("koo",[],VoidType(),Block([MethCall(Id("b"),"koo",[])]))),
            FuncDecl("foo",[],VoidType(),Block(
                [
                    VarDecl("x",Id("VO"), None),
                    ConstDecl("b",None,MethCall(Id("x"),"foo",[])),MethCall(Id("x"),"koo",[])]
                ))])
        self.assertTrue(TestChecker.test(input, "Undeclared Method: koo", inspect.stack()[0].function))

    def test_072(self):
        """
        var v int = 1.02;
        """
        input = Program([VarDecl("v",IntType(),FloatLiteral(1.02))])
        self.assertTrue(TestChecker.test(input, "Type Mismatch: VarDecl(v,IntType,FloatLiteral(1.02))", inspect.stack()[0].function))

    def test_074(self):
        """
        var v string = true;
        """
        input = Program([VarDecl("v",StringType(),BooleanLiteral(True))])
        self.assertTrue(TestChecker.test(input, "Type Mismatch: VarDecl(v,StringType,BooleanLiteral(true))", inspect.stack()[0].function))

    def test_076(self):
        """
type S1 struct {votien int;}
type S2 struct {votien int;}

var v S1;
const x = v;
var z S1 = x;
var k S2 = x;
        :return:
        """
        input = Program([
            StructType("S1",[("votien",IntType())],[]),
            StructType("S2",[("votien",IntType())],[]),
            VarDecl("v",Id("S1"), None),
            ConstDecl("x",None,Id("v")),VarDecl("z",Id("S1"),Id("x")),VarDecl("k",Id("S2"),Id("x"))
        ])
        self.assertTrue(TestChecker.test(input, "Type Mismatch: VarDecl(k,Id(S2),Id(x))", inspect.stack()[0].function))

    def test_078(self):
        """
type S1 struct {votien int;}
type S2 struct {votien int;}
type I1 interface {votien();}
type I2 interface {votien();}

func (s S1) votien() {return;}

var a S1;
var b S2;
var c I1 = a;
var d I2 = b;
        :return:
        """
        input = Program([
            StructType("S1",[("votien",IntType())],[]),
            StructType("S2",[("votien",IntType())],[]),
            InterfaceType("I1",[Prototype("votien",[],VoidType())]),
            InterfaceType("I2",[Prototype("votien",[],VoidType())]),
            MethodDecl("s",Id("S1"),FuncDecl("votien",[],VoidType(),
                 Block([Return(None)]))),

            VarDecl("a",Id("S1"), None),
            VarDecl("b",Id("S2"), None),
            VarDecl("c",Id("I1"),Id("a")),
            VarDecl("d",Id("I2"),Id("b"))])
        self.assertTrue(TestChecker.test(input, "Type Mismatch: VarDecl(d,Id(I2),Id(b))", inspect.stack()[0].function))

    def test_079(self):
        """
type S1 struct {votien int;}
type S2 struct {votien int;}
type I1 interface {votien();}
type I2 interface {votien() int;}

func (s S1) votien() {return;}

var a S1;
var b S2;
var c I2 = a;
        :return:
        """
        input = Program([
            StructType("S1",[("votien",IntType())],[]),
            StructType("S2",[("votien",IntType())],[]),
            InterfaceType("I1",[Prototype("votien",[],VoidType())]),
            InterfaceType("I2",[Prototype("votien",[],IntType())]),

            MethodDecl("s",Id("S1"),FuncDecl("votien",[],VoidType(),Block([Return(None)]))),
            VarDecl("a",Id("S1"), None),VarDecl("b",Id("S2"), None),VarDecl("c",Id("I2"),Id("a"))])
        self.assertTrue(TestChecker.test(input, "Type Mismatch: VarDecl(c,Id(I2),Id(a))", inspect.stack()[0].function))

    def test_080(self):
        """
type S1 struct {votien int;}
type S2 struct {votien int;}
type I1 interface {votien() S1;}
type I2 interface {votien() S2;}

func (s S1) votien() S1 {return s;}

var a S1;
var c I1 = a;
var d I2 = a;
        :return:
        """
        input = Program([
            StructType("S1",[("votien",IntType())],[]),
            StructType("S2",[("votien",IntType())],[]),
            InterfaceType("I1",[Prototype("votien",[],Id("S1"))]),
            InterfaceType("I2",[Prototype("votien",[],Id("S2"))]),
            MethodDecl("s",Id("S1"),FuncDecl("votien",[],Id("S1"),Block([
                Return(Id("s"))]))),
            VarDecl("a",Id("S1"), None),
            VarDecl("c",Id("I1"),Id("a")),
            VarDecl("d",Id("I2"),Id("a"))])
        self.assertTrue(TestChecker.test(input, "Type Mismatch: VarDecl(d,Id(I2),Id(a))", inspect.stack()[0].function))

    def test_082(self):
        """
type S1 struct {votien int;}
type S2 struct {votien int;}
type I1 interface {votien(e, e int) S1;}
type I2 interface {votien(a int, b float) S1;}

func (s S1) votien(a, b int) S1 {return s;}

var a S1;
var c I1 = a;
var d I2 = a;
        :return:
        """
        input = Program([
            StructType("S1",[("votien",IntType())],[]),
            StructType("S2",[("votien",IntType())],[]),
            InterfaceType("I1",[Prototype("votien",[IntType(),IntType()],Id("S1"))]),
            InterfaceType("I2",[Prototype("votien",[IntType(),FloatType()],Id("S1"))]),
            MethodDecl("s",Id("S1"),FuncDecl("votien",[ParamDecl("a",IntType()),ParamDecl("b",IntType())],Id("S1"),Block([Return(Id("s"))]))),
            VarDecl("a",Id("S1"), None),
            VarDecl("c",Id("I1"),Id("a")),
            VarDecl("d",Id("I2"),Id("a"))])
        self.assertTrue(TestChecker.test(input, "Type Mismatch: VarDecl(d,Id(I2),Id(a))", inspect.stack()[0].function))

    def test_086(self):
        """
func foo(){
if (true) {
     var a float = 1.02;
} else {
    var a int = 1.02;
}
}
        """
        input = Program([
            FuncDecl("foo",[],VoidType(),Block([
                If(BooleanLiteral(True), Block([
                    VarDecl("a",FloatType(),FloatLiteral(1.02))]), Block([
                    VarDecl("a",IntType(),FloatLiteral(1.02))]
                ))]))
        ])
        self.assertTrue(TestChecker.test(input, "Type Mismatch: VarDecl(a,IntType,FloatLiteral(1.02))", inspect.stack()[0].function))

    def test_090(self):
        """
type TIEN struct {v int;}
var v TIEN;
func foo(){
    for 1 {
         var a int = 1.02;
    }
}
        :return:
        """
        input = Program([
            StructType("TIEN",[("v",IntType())],[]),
            VarDecl("v",Id("TIEN"), None),
            FuncDecl("foo",[],VoidType(),Block([
                ForBasic(IntLiteral(1),Block([
                    VarDecl("a",IntType(),FloatLiteral(1.02))]))]))])
        self.assertTrue(TestChecker.test(input, "Type Mismatch: For(IntLiteral(1),Block([VarDecl(a,IntType,FloatLiteral(1.02))]))", inspect.stack()[0].function))

    def test_092(self):
        """
func foo(){
    return
}
func foo1() int{
    return 1
}
func foo2() float{
    return 2
}
        :return:
        """
        input = Program([
            FuncDecl("foo",[],VoidType(),Block([Return(None)])),
            FuncDecl("foo1",[],IntType(),Block([Return(IntLiteral(1))])),
            FuncDecl("foo2",[],FloatType(),Block([Return(IntLiteral(2))]))])
        self.assertTrue(TestChecker.test(input, "Type Mismatch: Return(IntLiteral(2))", inspect.stack()[0].function))

    def test_095(self):
        """
type S1 struct {v int;}

var a = S1 {v :  z}
        :return:
        """
        input = Program([
            StructType("S1",[("v",IntType())],[]),
            VarDecl("a", None,StructLiteral("S1",[("v",Id("z"))]))])
        self.assertTrue(TestChecker.test(input, "Undeclared Identifier: z", inspect.stack()[0].function))

    def test_096(self):
        """
var a = [2] int {1, 2}
var c [2] float = a
        :return:
        """
        input = Program([
            VarDecl("a", None,ArrayLiteral([IntLiteral(2)],IntType(),[IntLiteral(1),IntLiteral(2)])),
            VarDecl("c",ArrayType([IntLiteral(2)],FloatType()),Id("a"))])
        self.assertTrue(TestChecker.test(input, "VOTIEN",
                                         inspect.stack()[0].function))

    def test_097(self):
        """
var a = [2] float {1, 2}
var c [3] int = a
        :return:
        """
        input = Program([
            VarDecl("a", None,ArrayLiteral([IntLiteral(2)],FloatType(),[IntLiteral(1),IntLiteral(2)])),
            VarDecl("c",ArrayType([IntLiteral(3)],IntType()),Id("a"))
        ])
        self.assertTrue(TestChecker.test(input, "Type Mismatch: VarDecl(c,ArrayType(IntType,[IntLiteral(3)]),Id(a))",
                                         inspect.stack()[0].function))

    def test_099(self):
        """
type S1 struct {v int;}
var a = [1] S1  { S1 {v : z}};
        :return:
        """
        input = Program([
            StructType("S1",[("v",IntType())],[]),
            VarDecl("a", None,
                    ArrayLiteral([IntLiteral(1)],Id("S1"),[
                        StructLiteral("S1",[("v",Id("z"))])]))])
        self.assertTrue(TestChecker.test(input, "Undeclared Identifier: z", inspect.stack()[0].function))

    def test_101(self):
        """
var a [2][3] int;
var b = a[1][2];
var c int = b;
var d [1] string = b;
        :return:
        """
        input = Program([
            VarDecl("a",ArrayType([IntLiteral(2),IntLiteral(3)],IntType()), None),
            VarDecl("b", None,ArrayCell(Id("a"),[IntLiteral(1),IntLiteral(2)])),
            VarDecl("c",IntType(),Id("b")),
            VarDecl("d",ArrayType([IntLiteral(1)],StringType()),Id("b"))
        ])
        self.assertTrue(TestChecker.test(input, "Type Mismatch: VarDecl(d,ArrayType(StringType,[IntLiteral(1)]),Id(b))",
                                         inspect.stack()[0].function))

    def test_102(self):
        """
var a [2][3] int;
var b = a[1];
var c [3] int = b;
var d [3] string = b;
        """
        input = Program([
            VarDecl("a",ArrayType([IntLiteral(2),IntLiteral(3)],IntType()), None),
            VarDecl("b", None,ArrayCell(Id("a"),[IntLiteral(1)])),
            VarDecl("c",ArrayType([IntLiteral(3)],IntType()),Id("b")),
            VarDecl("d",ArrayType([IntLiteral(3)],StringType()),Id("b"))])
        self.assertTrue(TestChecker.test(input, "Type Mismatch: VarDecl(d,ArrayType(StringType,[IntLiteral(3)]),Id(b))",
                                         inspect.stack()[0].function))

    def test_105(self):
        """
type S1 struct {v int; x S1;}
var b S1;
var c = b.x.v;
var d = c.x;
        :return:
        """
        input = Program([
            StructType("S1",[("v",IntType()),("x",Id("S1"))],[]),
            VarDecl("b",Id("S1"), None),
            VarDecl("c", None,FieldAccess(FieldAccess(Id("b"),"x"),"v")),
            VarDecl("d", None,FieldAccess(Id("c"),"x"))])
        self.assertTrue(TestChecker.test(input, "Type Mismatch: FieldAccess(Id(c),x)", inspect.stack()[0].function))

    def test_107(self):
        """
type S1 struct {votien int;}
type I1 interface {votien();}
var a I1;
var c I1 = nil;
var d S1 = nil;
func foo(){
    c := a;
    a := nil;
}

var e int = nil;
        :return:
        """
        input = Program([
            StructType("S1",[("votien",IntType())],[]),
            InterfaceType("I1",[Prototype("votien",[],VoidType())]),
            VarDecl("a",Id("I1"), None),
            VarDecl("c",Id("I1"),NilLiteral()),
            VarDecl("d",Id("S1"),NilLiteral()),
            FuncDecl("foo",[],VoidType(),Block([
                Assign(Id("c"),Id("a")),
                Assign(Id("a"),NilLiteral())])),
            VarDecl("e",IntType(),NilLiteral())])
        self.assertTrue(TestChecker.test(input, "Type Mismatch: VarDecl(e,IntType,Nil)", inspect.stack()[0].function))

    def test_108(self):
        """
var a = -1;
var b = -1.02;
var c = - true;
        :return:
        """
        input = Program([
            VarDecl("a", None,UnaryOp("-",IntLiteral(1))),
            VarDecl("b", None,UnaryOp("-",FloatLiteral(1.02))),
            VarDecl("c", None,UnaryOp("-",BooleanLiteral(True)))])
        self.assertTrue(TestChecker.test(input, "Type Mismatch: UnaryOp(-,BooleanLiteral(true))", inspect.stack()[0].function))

    def test_110(self):
        """
var a = "1" + "2";
var c string = a;
var b = "1" + 1;
        :return:
        """
        input = Program([
            VarDecl("a", None,BinaryOp("+", StringLiteral("1"), StringLiteral("2"))),
            VarDecl("c",StringType(),Id("a")),
            VarDecl("b", None,BinaryOp("+", StringLiteral("1"), IntLiteral(1)))])
        self.assertTrue(TestChecker.test(input, "Type Mismatch: BinaryOp(StringLiteral(1),+,IntLiteral(1))", inspect.stack()[0].function))

    def test_111(self):
        """
var a = 1 + 2.0;
var b = 1 + 1;
func foo() int {
    return b;
    return a;
}
        :return:
        """
        input = Program([
            VarDecl("a", None,BinaryOp("+", IntLiteral(1), FloatLiteral(2.0))),
            VarDecl("b", None,BinaryOp("+", IntLiteral(1), IntLiteral(1))),
            FuncDecl("foo",[],IntType(),Block([Return(Id("b")),Return(Id("a"))]))])
        self.assertTrue(TestChecker.test(input, "Type Mismatch: Return(Id(a))", inspect.stack()[0].function))

    def test_112(self):
        """
var a = 1 + true;
        :return:
        """
        input = Program([VarDecl("a", None,BinaryOp("+", IntLiteral(1), BooleanLiteral(True)))])
        self.assertTrue(TestChecker.test(input, "Type Mismatch: BinaryOp(IntLiteral(1),+,BooleanLiteral(true))", inspect.stack()[0].function))

    def test_113(self):
        """
var a float = 1 * 2.0;
var b int = 1 / 2;
var c float = 1 / 2;
func foo() int {
    return b;
    return c;
}
        :return:
        """
        input = Program([
            VarDecl("a",FloatType(),BinaryOp("*", IntLiteral(1), FloatLiteral(2.0))),
            VarDecl("b",IntType(),BinaryOp("/", IntLiteral(1), IntLiteral(2))),
            VarDecl("c",FloatType(),BinaryOp("/", IntLiteral(1), IntLiteral(2))),
            FuncDecl("foo",[],IntType(),Block([
                Return(Id("b")),
                Return(Id("c"))]))])
        self.assertTrue(TestChecker.test(input, "Type Mismatch: Return(Id(c))", inspect.stack()[0].function))

    def test_115(self):
        """
var a int = 1 % 2;
var b int = 1 % 2.0;
        :return:
        """
        input = Program([
            VarDecl("a", IntType(), BinaryOp("%", IntLiteral(1), IntLiteral(2))),
            VarDecl("b", IntType(), BinaryOp("%", IntLiteral(1), FloatLiteral(2.0)))])
        self.assertTrue(TestChecker.test(input, "Type Mismatch: BinaryOp(IntLiteral(1),%,FloatLiteral(2.0))",
                                         inspect.stack()[0].function))

    def test_116(self):
        """
var a boolean = true && false || true;
var b boolean = true && 1;
        :return:
        """
        input = Program([
            VarDecl("a",BoolType(),BinaryOp("||", BinaryOp("&&", BooleanLiteral(True), BooleanLiteral(False)), BooleanLiteral(True))),
            VarDecl("b",BoolType(),BinaryOp("&&", BooleanLiteral(True), IntLiteral(1)))])
        self.assertTrue(TestChecker.test(input, "Type Mismatch: BinaryOp(BooleanLiteral(true),&&,IntLiteral(1))",
                                         inspect.stack()[0].function))

    def test_117(self):
        """
var a boolean = 1 > 2;
var b boolean = 1.0 < 2.0;
var c boolean = "1" == "2";
var d boolean = 1 > 2.0;
        :return:
        """
        input = Program([
            VarDecl("a",BoolType(),BinaryOp(">", IntLiteral(1), IntLiteral(2))),
            VarDecl("b",BoolType(),BinaryOp("<", FloatLiteral(1.0), FloatLiteral(2.0))),
            VarDecl("c",BoolType(),BinaryOp("==", StringLiteral("1"), StringLiteral("2"))),
            VarDecl("d",BoolType(),BinaryOp(">", IntLiteral(1), FloatLiteral(2.0)))])
        self.assertTrue(TestChecker.test(input, "Type Mismatch: BinaryOp(IntLiteral(1),>,FloatLiteral(2.0))",
                                         inspect.stack()[0].function))

    def test_120(self):
        """
func foo(){
    for var i int = 1; i < 10; i := 1.0 {
        return;
    }
}
        :return:
        """
        input = Program([
            FuncDecl("foo",[],VoidType(),Block([
                ForStep(VarDecl("i",IntType(),IntLiteral(1)),
                        BinaryOp("<", Id("i"), IntLiteral(10)),
                        Assign(Id("i"),FloatLiteral(1.0)),Block([Return(None)]))]))
        ])
        self.assertTrue(TestChecker.test(input, "Type Mismatch: Assign(Id(i),FloatLiteral(1.0))",
                                         inspect.stack()[0].function))

    def test_128(self):
        """
func foo() int {return 1;}
var a float = foo(1 + 1);
        :return:
        """
        input = Program([
            FuncDecl("foo",[],IntType(),Block([Return(IntLiteral(1))])),
            VarDecl("a",FloatType(),FuncCall("foo",[BinaryOp("+", IntLiteral(1), IntLiteral(1))]))])
        self.assertTrue(TestChecker.test(input, "Type Mismatch: FuncCall(foo,[BinaryOp(IntLiteral(1),+,IntLiteral(1))])",
                                         inspect.stack()[0].function))

    def test_129(self):
        """
func foo(a int) int {return 1;}

var a int = foo(1 + 1);
var b = foo(1.0);
        :return:
        """
        input = Program([
            FuncDecl("foo",[ParamDecl("a",IntType())],IntType(),Block([Return(IntLiteral(1))])),
            VarDecl("a",IntType(),FuncCall("foo",[BinaryOp("+", IntLiteral(1), IntLiteral(1))])),
            VarDecl("b", None,FuncCall("foo",[FloatLiteral(1.0)]))])
        self.assertTrue(TestChecker.test(input, "Type Mismatch: FuncCall(foo,[FloatLiteral(1.0)])",
                                         inspect.stack()[0].function))

    def test_130(self):
        """
type S1 struct {votien1 int;}
type I1 interface {votien() int;}
func (s S1) votien() int {return 1;}

var i I1;
var s S1;
var a int = i.votien();
var b int = s.votien();
var c int = a.votien();
        :return:
        """
        input = Program([
            StructType("S1",[("votien1",IntType())],[]),
            InterfaceType("I1",[Prototype("votien",[],IntType())]),
            MethodDecl("s",Id("S1"),FuncDecl("votien",[],IntType(),Block([Return(IntLiteral(1))]))),
            VarDecl("i",Id("I1"), None),
            VarDecl("s",Id("S1"), None),
            VarDecl("a",IntType(),MethCall(Id("i"),"votien",[])),
            VarDecl("b",IntType(),MethCall(Id("s"),"votien",[])),
            VarDecl("c",IntType(),MethCall(Id("a"),"votien",[]))])
        self.assertTrue(TestChecker.test(input, "Type Mismatch: MethodCall(Id(a),votien,[])", inspect.stack()[0].function))

    def test_132(self):
        """
type S1 struct {votien1 int;}
type I1 interface {votien(a int) int;}
func (s S1) votien( a int) int {return 1;}

var s S1;
var a int = s.votien(1);
var b int = s.votien(1.0);
        :return:
        """
        input = Program([
            StructType("S1",[("votien1",IntType())],[]),
            InterfaceType("I1",[Prototype("votien",[IntType()],IntType())]),
            MethodDecl("s",Id("S1"),FuncDecl("votien",[ParamDecl("a",IntType())],IntType(),Block([Return(IntLiteral(1))]))),
            VarDecl("s",Id("S1"), None),
            VarDecl("a",IntType(),MethCall(Id("s"),"votien",[IntLiteral(1)])),
            VarDecl("b", IntType(),MethCall(Id("s"),"votien",[FloatLiteral(1.0)]))])
        self.assertTrue(TestChecker.test(input, "Type Mismatch: MethodCall(Id(s),votien,[FloatLiteral(1.0)])",
                                         inspect.stack()[0].function))

    def test_139(self):
        """
type Person struct {
    name string ;
    age int ;
}

func  votien()  {
    var person = Person{name: "Alice", age: 30}
    person.name := "John";
    person.age := 30;
    putStringLn(person.name)
    putStringLn(person.Greet())
}

func (p Person) Greet() string {
return "Hello, " + p.name
}
        :return:
        """
        input = Program([
            StructType("Person",[("name",StringType()),("age",IntType())],[]),
            FuncDecl("votien",[],VoidType(),Block([
                VarDecl("person", None,StructLiteral("Person",[("name",StringLiteral("Alice")),("age",IntLiteral(30))])),
                Assign(FieldAccess(Id("person"),"name"),StringLiteral("John")),
                Assign(FieldAccess(Id("person"),"age"),IntLiteral(30)),
                FuncCall("putStringLn",[FieldAccess(Id("person"),"name")]),
                FuncCall("putStringLn",[MethCall(Id("person"),"Greet",[])])
            ])),
            MethodDecl("p",Id("Person"),FuncDecl("Greet",[],StringType(),Block([
                Return(BinaryOp("+", StringLiteral("Hello, "), FieldAccess(Id("p"),"name")))
            ])))])
        self.assertTrue(TestChecker.test(input, "VOTIEN",
                                         inspect.stack()[0].function))

    def test_143(self):
        """
var a TIEN;
func foo() TIEN {
    return a;
    return TIEN;
}

type TIEN struct {tien int;}
        """
        input = Program([
            VarDecl("a",Id("TIEN"), None),
            FuncDecl("foo",[],Id("TIEN"),Block([
                Return(Id("a")),
                Return(Id("TIEN"))])),
            StructType("TIEN",[("tien",IntType())],[])])
        self.assertTrue(TestChecker.test(input, """Undeclared Identifier: TIEN""", inspect.stack()[0].function))

    def test_151(self):
        """
type putLn struct {a int;};
        :return:
        """
        input = Program([StructType("putLn",[("a",IntType())],[])])
        self.assertTrue(TestChecker.test(input, "Redeclared Type: putLn", inspect.stack()[0].function))

    def test_158(self):
        """
func foo() [2] float {
    return [2] float {1.0, 2.0};
    return [2] int {1, 2};
}
        :return:
        """
        input = Program([
            FuncDecl("foo",[],ArrayType([IntLiteral(2)],FloatType()),Block([
                Return(ArrayLiteral([IntLiteral(2)],FloatType(),[FloatLiteral(1.0),FloatLiteral(2.0)])),
                Return(ArrayLiteral([IntLiteral(2)],IntType(),[IntLiteral(1),IntLiteral(2)]))]))])
        self.assertTrue(TestChecker.test(input,
                                         "Type Mismatch: Return(ArrayLiteral([IntLiteral(2)],IntType,[IntLiteral(1),IntLiteral(2)]))",
                                         inspect.stack()[0].function))

    def test_162(self):
        """
type TIEN struct {a [2]int;}
type VO interface {foo() int;}

func (v TIEN) foo() int {return 1;}

func foo(a VO) {
    var b VO = TIEN{a: [2]int{1, 2}};
    foo(b)
}
        :return:
        """
        input = Program([
            StructType("TIEN",[("a",ArrayType([IntLiteral(2)],IntType()))],[]),
            InterfaceType("VO",[Prototype("foo",[],IntType())]),
            MethodDecl("v",Id("TIEN"),FuncDecl("foo",[],IntType(),Block([Return(IntLiteral(1))]))),
            FuncDecl("foo",[ParamDecl("a",Id("VO"))],VoidType(),Block([
                VarDecl("b",Id("VO"),StructLiteral(
                    "TIEN",[("a",ArrayLiteral([IntLiteral(2)],IntType(),[IntLiteral(1),IntLiteral(2)]))])),
                FuncCall("foo",[Id("b")])]))
        ])
        self.assertTrue(TestChecker.test(input, "VOTIEN", inspect.stack()[0].function))

    def test_164(self):
        """
type TIEN struct {a [2]int;}
type VO interface {foo() int;}

func (v TIEN) foo() int {return 1;}

func foo(a VO) {
    var b = nil;
    foo(nil)
}
        :return:
        """
        input = Program([
            StructType("TIEN",[("a",ArrayType([IntLiteral(2)],IntType()))],[]),
            InterfaceType("VO",[Prototype("foo",[],IntType())]),
            MethodDecl("v",Id("TIEN"),FuncDecl("foo",[],IntType(),Block([Return(IntLiteral(1))]))),
            FuncDecl("foo",[ParamDecl("a",Id("VO"))],VoidType(),Block([
                VarDecl("b", None,NilLiteral()),
                FuncCall("foo",[NilLiteral()])]))])
        self.assertTrue(TestChecker.test(input, "VOTIEN", inspect.stack()[0].function))

    def test_165(self):
        """
type TIEN struct {a [2]int;}

func foo() TIEN {
    return nil
}
        :return:
        """
        input = Program([
            StructType("TIEN",[("a",ArrayType([IntLiteral(2)],IntType()))],[]),
            FuncDecl("foo",[],Id("TIEN"),Block([Return(NilLiteral())]))])
        self.assertTrue(TestChecker.test(input, "VOTIEN", inspect.stack()[0].function))

    def test_169(self):
        """
func foo() {
    var a [5][6] int;
    var b [2] float;
    b[2] := a[2][3]
    a[2][3] := b[2] + 1;
}
        :return:
        """
        input = Program([
            FuncDecl("foo",[],VoidType(),Block([
                VarDecl("a",ArrayType([IntLiteral(5),IntLiteral(6)],IntType()), None),
                VarDecl("b",ArrayType([IntLiteral(2)],FloatType()), None),
                Assign(ArrayCell(Id("b"),[IntLiteral(2)]),ArrayCell(Id("a"),[IntLiteral(2),IntLiteral(3)])),
                Assign(ArrayCell(Id("a"),[IntLiteral(2),IntLiteral(3)]),BinaryOp("+",ArrayCell(Id("b"),[IntLiteral(2)]),IntLiteral(1)))
            ]))])
        self.assertTrue(TestChecker.test(input,
            "Type Mismatch: Assign(ArrayCell(Id(a),[IntLiteral(2),IntLiteral(3)]),BinaryOp(ArrayCell(Id(b),[IntLiteral(2)]),+,IntLiteral(1)))",
                                         inspect.stack()[0].function))

    def test_174(self):
        """
var A = 1;
type A struct {a int;}
        :return:
        """
        input = Program([
            VarDecl("A", None, IntLiteral(1)),
            StructType("A",[("a",IntType())],[])])
        self.assertTrue(TestChecker.test(input, "Redeclared Type: A", inspect.stack()[0].function))

    def test_176(self):
        """
type A interface {foo();}
const A = 2;
        :return:
        """
        input = Program([
            InterfaceType("A",[Prototype("foo",[],VoidType())]),
            ConstDecl("A",None,IntLiteral(2))
        ])
        self.assertTrue(TestChecker.test(input, "Redeclared Constant: A", inspect.stack()[0].function))

    def test_181(self):
        """
func foo(a [2] float) {
    foo([2] float {1.0,2.0})
    foo([2] int {1,2})
}
        :return:
        """
        input = Program([
            FuncDecl("foo",[ParamDecl("a",ArrayType([IntLiteral(2)],FloatType()))],VoidType(),Block([
                FuncCall("foo",[ArrayLiteral([IntLiteral(2)],FloatType(),[FloatLiteral(1.0),FloatLiteral(2.0)])]),
                FuncCall("foo",[ArrayLiteral([IntLiteral(2)],IntType(),[IntLiteral(1),IntLiteral(2)])])
            ]))])
        self.assertTrue(TestChecker.test(input, "Type Mismatch: FuncCall(foo,[ArrayLiteral([IntLiteral(2)],IntType,[IntLiteral(1),IntLiteral(2)])])",
                                         inspect.stack()[0].function))

    def test_183(self):
        """
func votien(a  [2]int ) {
    votien([3] int {1,2,3})
}
        :return:
        """
        input = Program([
            FuncDecl("votien",[ParamDecl("a",ArrayType([IntLiteral(2)],IntType()))],VoidType(),Block([
                FuncCall("votien",[ArrayLiteral([IntLiteral(3)],IntType(),[IntLiteral(1),IntLiteral(2),IntLiteral(3)])])
            ]))])
        self.assertTrue(TestChecker.test(input, "Type Mismatch: FuncCall(votien,[ArrayLiteral([IntLiteral(3)],IntType,[IntLiteral(1),IntLiteral(2),IntLiteral(3)])])",
                                         inspect.stack()[0].function))

    def test_184(self):
        """
var a [1 + 9] int;
var b [10] int = a;
        :return:
        """
        input = Program([
            VarDecl("a",ArrayType([BinaryOp("+",IntLiteral(1),IntLiteral(9))],IntType()), None),
            VarDecl("b",ArrayType([IntLiteral(10)],IntType()),Id("a"))])
        self.assertTrue(TestChecker.test(input, "VOTIEN",
                                         inspect.stack()[0].function))