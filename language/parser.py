from langkit.parsers import Grammar, List, NoBacktrack, Opt, Or, Pick

from language import rflx_ast as ast
from language.lexer import rflx_lexer as lexer

grammar = Grammar("main_rule")

grammar.add_rules(
    main_rule=Opt(grammar.specification),
    unqualified_identifier=ast.UnqualifiedID(
        Or(
            lexer.Package,
            lexer.Is,
            lexer.If,
            lexer.End,
            lexer.Null,
            lexer.Type,
            lexer.Range,
            lexer.With,
            lexer.Mod,
            lexer.Message,
            lexer.Then,
            lexer.Sequence,
            lexer.Of,
            lexer.In,
            lexer.Not,
            lexer.New,
            lexer.For,
            lexer.When,
            lexer.Where,
            lexer.Use,
            lexer.All,
            lexer.Some,
            lexer.Generic,
            lexer.Session,
            lexer.Begin,
            lexer.Private,
            lexer.Return,
            lexer.Function,
            lexer.State,
            lexer.Transition,
            lexer.Goto,
            lexer.Exception,
            lexer.Renames,
            lexer.Channel,
            lexer.Readable,
            lexer.Writable,
            lexer.Desc,
            lexer.Append,
            lexer.Extend,
            lexer.Read,
            lexer.Write,
            lexer.Reset,
            lexer.Checksum,
            lexer.ValidChecksum,
            lexer.HasData,
            lexer.Head,
            lexer.Opaque,
            lexer.Present,
            lexer.Valid,
            lexer.Initial,
            lexer.Final,
            lexer.And,
            lexer.Or,
            lexer.UnqualifiedIdentifier,
        )
    ),
    qualified_identifier=ast.ID(
        Opt(grammar.unqualified_identifier, "::"), grammar.unqualified_identifier
    ),
    numeric_literal=ast.NumericLiteral(lexer.Numeral),
    variable=ast.Variable(grammar.qualified_identifier),
    sequence_aggregate=ast.SequenceAggregate(
        "[", List(grammar.numeric_literal, sep=",", empty_valid=True), "]"
    ),
    string_literal=ast.StringLiteral(lexer.StringLiteral),
    concatenation=Or(
        ast.Concatenation(
            grammar.concatenation,
            "&",
            NoBacktrack(),
            Or(grammar.sequence_aggregate, grammar.string_literal),
        ),
        Or(grammar.sequence_aggregate, grammar.string_literal),
    ),
    primary=Or(
        grammar.concatenation,
        grammar.numeric_literal,
        grammar.string_literal,
        grammar.variable,
        grammar.paren_expression,
    ),
    paren_expression=ast.ParenExpression("(", grammar.expression, ")"),
    suffix=Or(
        ast.Attribute(
            grammar.suffix,
            "'",
            Or(
                # pylint: disable=no-member
                ast.Attr.alt_first(lexer.First),
                ast.Attr.alt_size(lexer.Size),
                ast.Attr.alt_last(lexer.Last),
                ast.Attr.alt_valid_checksum(lexer.ValidChecksum),
            ),
        ),
        grammar.primary,
    ),
    factor=Or(
        # pylint: disable=no-member
        ast.BinOp(grammar.primary, ast.Op.alt_pow("**"), NoBacktrack(), grammar.primary),
        grammar.suffix,
    ),
    term=Or(
        ast.BinOp(
            grammar.term,
            Or(
                # pylint: disable=no-member
                ast.Op.alt_mul("*"),
                ast.Op.alt_div("/"),
                ast.Op.alt_mod("mod"),
            ),
            NoBacktrack(),
            grammar.factor,
        ),
        grammar.factor,
    ),
    unop_term=Or(ast.Negation("-", NoBacktrack(), grammar.term), grammar.term),
    simple_expr=Or(
        ast.BinOp(
            grammar.simple_expr,
            Or(
                # pylint: disable=no-member
                ast.Op.alt_add("+"),
                ast.Op.alt_sub("-"),
            ),
            NoBacktrack(),
            grammar.unop_term,
        ),
        grammar.unop_term,
    ),
    relation=Or(
        ast.BinOp(
            grammar.relation,
            Or(
                # pylint: disable=no-member
                ast.Op.alt_eq("="),
                ast.Op.alt_neq("/="),
                ast.Op.alt_le("<="),
                ast.Op.alt_lt("<"),
                ast.Op.alt_ge(">="),
                ast.Op.alt_gt(">"),
            ),
            NoBacktrack(),
            grammar.simple_expr,
        ),
        grammar.simple_expr,
    ),
    unop_expression=Or(ast.Not(lexer.Not, NoBacktrack(), grammar.relation), grammar.relation),
    expression=Or(
        ast.BinOp(
            grammar.expression,
            Or(
                # pylint: disable=no-member
                ast.Op.alt_and("and"),
                ast.Op.alt_or("or"),
            ),
            NoBacktrack(),
            grammar.unop_expression,
        ),
        grammar.unop_expression,
    ),
    quantified_expression=ast.QuantifiedExpression(
        "for",
        Or(
            # pylint: disable=no-member
            ast.Quantifier.alt_all("all"),
            ast.Quantifier.alt_some("some"),
        ),
        grammar.unqualified_identifier,
        "in",
        grammar.extended_expression,
        "=>",
        grammar.extended_expression,
    ),
    comprehension=ast.Comprehension(
        "[",
        "for",
        grammar.unqualified_identifier,
        "in",
        grammar.extended_expression,
        Opt("if", grammar.extended_expression),
        "=>",
        grammar.extended_expression,
        "]",
    ),
    call=ast.Call(
        grammar.unqualified_identifier,
        "(",
        List(grammar.extended_expression, sep=","),
        ")",
    ),
    conversion=ast.Conversion(grammar.qualified_identifier, "(", grammar.extended_expression, ")"),
    null_message_aggregate=ast.NullMessageAggregate("null", "message"),
    message_aggregate_association=ast.MessageAggregateAssociation(
        grammar.unqualified_identifier, "=>", grammar.extended_expression
    ),
    message_aggregate_association_list=ast.MessageAggregateAssociations(
        List(grammar.message_aggregate_association, sep=",")
    ),
    message_aggregate=ast.MessageAggregate(
        grammar.qualified_identifier,
        "'",
        "(",
        Or(grammar.null_message_aggregate, grammar.message_aggregate_association_list),
        ")",
    ),
    extended_primary=Or(
        grammar.concatenation,
        grammar.numeric_literal,
        grammar.string_literal,
        grammar.quantified_expression,
        grammar.comprehension,
        grammar.call,
        grammar.conversion,
        grammar.message_aggregate,
        grammar.variable,
        grammar.extended_paren_expression,
    ),
    extended_paren_expression=ast.ParenExpression("(", grammar.extended_expression, ")"),
    extended_suffix=Or(
        ast.Select(
            grammar.extended_suffix,
            ".",
            NoBacktrack(),
            grammar.unqualified_identifier,
        ),
        ast.Attribute(
            grammar.extended_suffix,
            "'",
            Or(
                # pylint: disable=no-member
                ast.Attr.alt_first(lexer.First),
                ast.Attr.alt_size(lexer.Size),
                ast.Attr.alt_last(lexer.Last),
                ast.Attr.alt_valid_checksum(lexer.ValidChecksum),
                ast.Attr.alt_has_data(lexer.HasData),
                ast.Attr.alt_head(lexer.Head),
                ast.Attr.alt_opaque(lexer.Opaque),
                ast.Attr.alt_present(lexer.Present),
                ast.Attr.alt_valid(lexer.Valid),
            ),
        ),
        ast.Binding(
            grammar.extended_suffix,
            "where",
            List(
                ast.TermAssoc(grammar.unqualified_identifier, "=", grammar.extended_expression),
                sep=",",
            ),
        ),
        grammar.extended_primary,
    ),
    extended_factor=Or(
        ast.BinOp(
            grammar.extended_factor,
            Or(
                # pylint: disable=no-member
                ast.Op.alt_pow("**"),
            ),
            NoBacktrack(),
            grammar.extended_suffix,
        ),
        grammar.extended_suffix,
    ),
    extended_term=Or(
        ast.BinOp(
            grammar.extended_term,
            Or(
                # pylint: disable=no-member
                ast.Op.alt_mul("*"),
                ast.Op.alt_div("/"),
                ast.Op.alt_mod("mod"),
            ),
            NoBacktrack(),
            grammar.extended_factor,
        ),
        grammar.extended_factor,
    ),
    extended_unop_term=Or(
        ast.Negation("-", NoBacktrack(), grammar.extended_term),
        grammar.extended_term,
    ),
    extended_simple_expr=Or(
        ast.BinOp(
            grammar.extended_simple_expr,
            Or(
                # pylint: disable=no-member
                ast.Op.alt_add("+"),
                ast.Op.alt_sub("-"),
            ),
            NoBacktrack(),
            grammar.extended_unop_term,
        ),
        grammar.extended_unop_term,
    ),
    extended_relation=Or(
        ast.BinOp(
            grammar.extended_relation,
            Or(
                # pylint: disable=no-member
                ast.Op.alt_eq("="),
                ast.Op.alt_neq("/="),
                ast.Op.alt_le("<="),
                ast.Op.alt_lt("<"),
                ast.Op.alt_ge(">="),
                ast.Op.alt_gt(">"),
                ast.Op.alt_in("in"),
                ast.Op.alt_notin("not", "in"),
            ),
            NoBacktrack(),
            grammar.extended_simple_expr,
        ),
        grammar.extended_simple_expr,
    ),
    extended_unop_expression=Or(
        ast.Not(lexer.Not, NoBacktrack(), grammar.extended_relation),
        grammar.extended_relation,
    ),
    extended_expression=Or(
        ast.BinOp(
            grammar.extended_expression,
            Or(
                # pylint: disable=no-member
                ast.Op.alt_and("and"),
                ast.Op.alt_or("or"),
            ),
            NoBacktrack(),
            grammar.extended_unop_expression,
        ),
        grammar.extended_unop_expression,
    ),
    aspect=ast.Aspect(grammar.unqualified_identifier, Opt("=>", grammar.expression)),
    range_type_definition=ast.RangeTypeDef(
        "range",
        grammar.expression,
        "..",
        grammar.expression,
        "with",
        grammar.aspect,
    ),
    modular_type_definition=ast.ModularTypeDef("mod", grammar.expression),
    integer_type_definition=Or(grammar.range_type_definition, grammar.modular_type_definition),
    if_condition=Pick("if", grammar.expression),
    extended_if_condition=Pick("if", grammar.extended_expression),
    then=ast.Then(
        "then",
        Or(ast.NullID("null"), grammar.unqualified_identifier),
        Opt("with", List(grammar.aspect, sep=",")),
        Opt(grammar.if_condition),
    ),
    type_argument=ast.TypeArgument(grammar.unqualified_identifier, "=>", grammar.expression),
    null_message_field=ast.NullMessageField("null", grammar.then, ";"),
    message_field=ast.MessageField(
        grammar.unqualified_identifier,
        ":",
        grammar.qualified_identifier,
        Opt("(", List(grammar.type_argument, sep=","), ")"),
        Opt("with", List(grammar.aspect, sep=",")),
        Opt(grammar.if_condition),
        List(grammar.then, empty_valid=True),
        ";",
    ),
    message_field_list=ast.MessageFields(
        Opt(grammar.null_message_field), List(grammar.message_field)
    ),
    value_range=ast.ChecksumValueRange(grammar.expression, "..", grammar.expression),
    checksum_association=ast.ChecksumAssoc(
        grammar.unqualified_identifier,
        "=>",
        "(",
        List(Or(grammar.value_range, ast.ChecksumVal(grammar.expression)), sep=","),
        ")",
    ),
    checksum_aspect=ast.ChecksumAspect(
        "Checksum", "=>", "(", List(grammar.checksum_association, sep=","), ")"
    ),
    byte_order_aspect=ast.ByteOrderAspect(
        "Byte_Order",
        "=>",
        Or(
            # pylint: disable=no-member
            ast.ByteOrderType.alt_highorderfirst("High_Order_First"),
            ast.ByteOrderType.alt_loworderfirst("Low_Order_First"),
        ),
    ),
    message_aspect_list=List(Or(grammar.checksum_aspect, grammar.byte_order_aspect), sep=","),
    message_type_definition=Or(
        ast.MessageTypeDef(
            "message",
            grammar.message_field_list,
            "end",
            "message",
            Opt("with", grammar.message_aspect_list),
        ),
        ast.NullMessageTypeDef("null", "message"),
    ),
    positional_enumeration=ast.PositionalEnumerationDef(
        List(grammar.unqualified_identifier, sep=",")
    ),
    element_value_association=ast.ElementValueAssoc(
        grammar.unqualified_identifier, "=>", grammar.numeric_literal
    ),
    named_enumeration=ast.NamedEnumerationDef(List(grammar.element_value_association, sep=",")),
    enumeration_aspects=List(Or(grammar.aspect, grammar.aspect), sep=","),
    enumeration_type_definition=ast.EnumerationTypeDef(
        "(",
        Or(grammar.named_enumeration, grammar.positional_enumeration),
        ")",
        "with",
        grammar.enumeration_aspects,
    ),
    type_derivation_definition=ast.TypeDerivationDef(
        "new",
        grammar.qualified_identifier,
    ),
    sequence_type_definition=ast.SequenceTypeDef(
        "sequence",
        "of",
        grammar.qualified_identifier,
    ),
    type_declaration=ast.TypeDecl(
        "type",
        grammar.unqualified_identifier,
        Opt(grammar.parameter_list),
        "is",
        Or(
            grammar.enumeration_type_definition,
            grammar.integer_type_definition,
            grammar.message_type_definition,
            grammar.type_derivation_definition,
            grammar.sequence_type_definition,
        ),
    ),
    type_refinement=ast.RefinementDecl(
        "for",
        grammar.qualified_identifier,
        "use",
        "(",
        grammar.unqualified_identifier,
        "=>",
        grammar.qualified_identifier,
        ")",
        Opt(grammar.if_condition),
    ),
    private_type_declaration=ast.FormalPrivateTypeDecl(
        "type", grammar.unqualified_identifier, "is", "private"
    ),
    parameter=ast.Parameter(grammar.unqualified_identifier, ":", grammar.qualified_identifier),
    parameter_list=ast.Parameters("(", List(grammar.parameter, sep=";"), ")"),
    formal_function_declaration=ast.FormalFunctionDecl(
        "with",
        "function",
        grammar.unqualified_identifier,
        Opt(grammar.parameter_list),
        "return",
        grammar.qualified_identifier,
    ),
    channel_declaration=ast.FormalChannelDecl(
        grammar.unqualified_identifier,
        ":",
        "Channel",
        "with",
        List(Or(ast.Readable("Readable"), ast.Writable("Writable")), sep=","),
    ),
    session_parameter=Or(
        grammar.private_type_declaration,
        grammar.formal_function_declaration,
        grammar.channel_declaration,
    ),
    session_aspects=ast.SessionAspects(
        "with",
        "Initial",
        "=>",
        grammar.unqualified_identifier,
        ",",
        "Final",
        "=>",
        grammar.unqualified_identifier,
    ),
    renaming_declaration=ast.RenamingDecl(
        grammar.unqualified_identifier,
        ":",
        grammar.qualified_identifier,
        "renames",
        grammar.extended_expression,
    ),
    variable_declaration=ast.VariableDecl(
        grammar.unqualified_identifier,
        ":",
        grammar.qualified_identifier,
        Opt(":=", grammar.extended_expression),
    ),
    declaration=Or(grammar.renaming_declaration, grammar.variable_declaration),
    description_aspect=ast.Description("Desc", "=>", grammar.string_literal),
    null_state_body=ast.NullStateBody("null", "state"),
    assignment_statement=ast.Assignment(
        grammar.unqualified_identifier, ":=", grammar.extended_expression
    ),
    list_attribute=ast.AttributeStatement(
        grammar.unqualified_identifier,
        "'",
        Or(
            # pylint: disable=no-member
            ast.AttrStmt.alt_append("Append"),
            ast.AttrStmt.alt_extend("Extend"),
            ast.AttrStmt.alt_read("Read"),
            ast.AttrStmt.alt_write("Write"),
        ),
        "(",
        grammar.extended_expression,
        ")",
    ),
    reset=ast.Reset(
        grammar.unqualified_identifier,
        "'",
        "Reset",
        Opt("(", List(grammar.message_aggregate_association, sep=","), ")"),
    ),
    attribute_statement=Or(grammar.list_attribute, grammar.reset),
    action=Or(grammar.assignment_statement, grammar.attribute_statement),
    conditional_transition=ast.ConditionalTransition(
        "goto",
        grammar.unqualified_identifier,
        Opt("with", grammar.description_aspect),
        grammar.extended_if_condition,
    ),
    transition=ast.Transition(
        "goto",
        grammar.unqualified_identifier,
        Opt("with", grammar.description_aspect),
    ),
    state_body=ast.StateBody(
        Opt(List(grammar.declaration, sep=";"), ";"),
        "begin",
        Opt(List(grammar.action, sep=";"), ";"),
        "transition",
        List(grammar.conditional_transition, empty_valid=True),
        grammar.transition,
        Opt("exception", grammar.transition),
        "end",
        grammar.unqualified_identifier,
    ),
    state=ast.State(
        "state",
        grammar.unqualified_identifier,
        Opt("with", grammar.description_aspect),
        "is",
        Or(grammar.null_state_body, grammar.state_body),
    ),
    session_declaration=ast.SessionDecl(
        "generic",
        Opt(List(grammar.session_parameter, sep=";"), ";"),
        "session",
        grammar.unqualified_identifier,
        grammar.session_aspects,
        "is",
        Opt(List(grammar.declaration, sep=";"), ";"),
        "begin",
        Opt(List(grammar.state, sep=";"), ";"),
        "end",
        grammar.unqualified_identifier,
    ),
    basic_declaration=Or(
        grammar.type_declaration, grammar.type_refinement, grammar.session_declaration
    ),
    basic_declarations=Pick(List(grammar.basic_declaration, sep=";"), ";"),
    package_declaration=ast.Package(
        "package",
        grammar.unqualified_identifier,
        "is",
        Opt(grammar.basic_declarations),
        "end",
        grammar.unqualified_identifier,
        ";",
    ),
    context_item=ast.ContextItem("with", grammar.unqualified_identifier, ";"),
    context_clause=List(grammar.context_item, empty_valid=True),
    specification=ast.Specification(grammar.context_clause, grammar.package_declaration),
)
