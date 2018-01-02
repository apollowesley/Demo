package com.kyl.ps.exception;

public class DBException extends Exception {

	/** serialVersionUID*/
	private static final long serialVersionUID = -7589414946520065257L;

	public DBException() {
		super();
	}

	public DBException(String message, Throwable cause) {
		super(message, cause);
	}

	public DBException(String message) {
		super(message);
	}

	public DBException(Throwable cause) {
		super(cause);
	}

}
