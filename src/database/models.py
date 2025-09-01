# Database models 
from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Cliente(Base):
    __tablename__ = 'clientes'
    id = Column(Integer, primary_key=True)
    nome = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    documento = Column(String(50), unique=False)
    data_criacao = Column(DateTime, nullable=False)
    
    assinaturas = relationship('Assinatura', back_populates='cliente')
    transacoes = relationship('Transacao', back_populates='cliente')

class Assinatura(Base):
    __tablename__ = 'assinaturas'
    id = Column(Integer, primary_key=True)
    id_assinatura_origem = Column(String(255), unique=True, nullable=False)
    plataforma = Column(String(50), nullable=False)
    cliente_id = Column(Integer, ForeignKey('clientes.id'), nullable=False)
    produto_nome = Column(String(255))
    nome_oferta = Column(String(255), nullable=True)
    status = Column(String(50), nullable=False)
    data_inicio = Column(DateTime)
    data_proxima_cobranca = Column(DateTime)
    data_cancelamento = Column(DateTime)
    data_expiracao_acesso = Column(DateTime, nullable=False)
    valor_mensal = Column(Numeric(10, 2))
    valor_anual = Column(Numeric(10, 2))
    ultima_atualizacao = Column(DateTime)

    cliente = relationship('Cliente', back_populates='assinaturas')
    transacoes = relationship('Transacao', back_populates='assinatura')

class Transacao(Base):
    __tablename__ = 'transacoes'
    id = Column(Integer, primary_key=True)
    id_transacao_origem = Column(String(255), unique=False, nullable=False)
    assinatura_id = Column(Integer, ForeignKey('assinaturas.id'), nullable=True)
    cliente_id = Column(Integer, ForeignKey('clientes.id'), nullable=False)
    plataforma = Column(String(50), nullable=False)
    status = Column(String(50), nullable=False)
    valor = Column(Numeric(10, 2))
    valor_liquido = Column(Numeric(10, 2))
    valor_bruto = Column(Numeric(10, 2))
    taxa_reembolso = Column(Numeric(10, 2))
    metodo_pagamento = Column(String(50))
    data_transacao = Column(DateTime, nullable=False)
    motivo_recusa = Column(Text)
    json_completo = Column(JSONB)
    tipo_recusa = Column(String(50), nullable=True)  # Novo campo para classificar recusas
    produto_nome = Column(String(255), nullable=True)  # Novo campo para identificar o produto (product_id)
    nome_oferta = Column(String(255), nullable=True)  # Novo campo para identificar a oferta específica

    assinatura = relationship('Assinatura', back_populates='transacoes')
    cliente = relationship('Cliente', back_populates='transacoes') 